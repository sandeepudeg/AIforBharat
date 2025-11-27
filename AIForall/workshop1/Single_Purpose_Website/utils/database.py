import sqlite3
import json
import os
from datetime import datetime
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'contracts.db')

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Create contracts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                data TEXT NOT NULL,
                status TEXT DEFAULT 'saved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()

@contextmanager
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_or_create_user(email):
    """Get or create user by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Try to get existing user
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE email = ?',
                         (datetime.now(), email))
            conn.commit()
            return user['id']
        else:
            # Create new user
            cursor.execute('INSERT INTO users (email) VALUES (?)', (email,))
            conn.commit()
            return cursor.lastrowid

def save_contract(user_id, title, contract_data):
    """Save a contract for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Convert contract data to JSON
        data_json = contract_data if isinstance(contract_data, str) else json.dumps(contract_data)
        
        cursor.execute('''
            INSERT INTO contracts (user_id, title, data)
            VALUES (?, ?, ?)
        ''', (user_id, title, data_json))
        
        conn.commit()
        return cursor.lastrowid

def update_contract(contract_id, title, contract_data):
    """Update an existing contract"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Convert contract data to JSON
        data_json = contract_data if isinstance(contract_data, str) else json.dumps(contract_data)
        
        cursor.execute('''
            UPDATE contracts
            SET title = ?, data = ?, updated_at = ?
            WHERE id = ?
        ''', (title, data_json, datetime.now(), contract_id))
        
        conn.commit()

def get_contract(contract_id):
    """Get a specific contract"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contracts WHERE id = ?', (contract_id,))
        contract = cursor.fetchone()
        
        if contract:
            return {
                'id': contract['id'],
                'title': contract['title'],
                'data': json.loads(contract['data']),
                'created_at': contract['created_at'],
                'updated_at': contract['updated_at']
            }
        return None

def get_user_contracts(user_id):
    """Get all contracts for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, created_at, updated_at
            FROM contracts
            WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))
        
        contracts = []
        for row in cursor.fetchall():
            contracts.append({
                'id': row['id'],
                'title': row['title'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        return contracts

def delete_contract(contract_id):
    """Delete a contract"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contracts WHERE id = ?', (contract_id,))
        conn.commit()

def get_user_by_email(email):
    """Get user ID by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        return user['id'] if user else None

def get_user_info(user_id):
    """Get user information"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            }
        return None

def update_user_name(user_id, name):
    """Update user name"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
        conn.commit()

def save_draft(user_id, title, contract_data):
    """Save a contract as draft"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Convert contract data to JSON
        data_json = contract_data if isinstance(contract_data, str) else json.dumps(contract_data)
        
        cursor.execute('''
            INSERT INTO contracts (user_id, title, data, status)
            VALUES (?, ?, ?, 'draft')
        ''', (user_id, title, data_json))
        
        conn.commit()
        return cursor.lastrowid

def update_draft(contract_id, title, contract_data):
    """Update a draft contract"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Convert contract data to JSON
        data_json = contract_data if isinstance(contract_data, str) else json.dumps(contract_data)
        
        cursor.execute('''
            UPDATE contracts
            SET title = ?, data = ?, updated_at = ?
            WHERE id = ? AND status = 'draft'
        ''', (title, data_json, datetime.now(), contract_id))
        
        conn.commit()

def publish_draft(contract_id):
    """Publish a draft contract"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE contracts
            SET status = 'saved', updated_at = ?
            WHERE id = ? AND status = 'draft'
        ''', (datetime.now(), contract_id))
        
        conn.commit()

def get_user_drafts(user_id):
    """Get all draft contracts for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, created_at, updated_at
            FROM contracts
            WHERE user_id = ? AND status = 'draft'
            ORDER BY updated_at DESC
        ''', (user_id,))
        
        contracts = []
        for row in cursor.fetchall():
            contracts.append({
                'id': row['id'],
                'title': row['title'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'status': 'draft'
            })
        
        return contracts
