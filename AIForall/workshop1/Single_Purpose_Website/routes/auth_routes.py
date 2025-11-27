from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import secrets
import os
from utils.database import get_or_create_user, get_user_by_email

bp = Blueprint('auth', __name__, url_prefix='/auth')

# In-memory storage for verification tokens (in production, use a database)
verification_tokens = {}

@bp.route('/signup', methods=['GET'])
def signup():
    """Display signup form"""
    if 'user_email' in session:
        return redirect(url_for('contract.generator'))
    return render_template('signup.html')

@bp.route('/signin', methods=['GET'])
def signin():
    """Display signin form"""
    if 'user_email' in session:
        return redirect(url_for('contract.generator'))
    return render_template('signin.html')

@bp.route('/signup', methods=['POST'])
def signup_submit():
    """Process signup form submission"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Validate email format
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Generate verification token
    token = secrets.token_urlsafe(32)
    verification_tokens[token] = {
        'email': email,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=1),
        'verified': False
    }
    
    # In production, send email with verification link
    # For now, return the token for testing
    verification_link = f"http://localhost:5000/auth/verify?token={token}"
    
    return jsonify({
        'message': 'Verification email sent',
        'verification_link': verification_link  # For testing only
    }), 200

@bp.route('/signin', methods=['POST'])
def signin_submit():
    """Process signin form submission"""
    data = request.get_json()
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Validate email format
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Generate verification token
    token = secrets.token_urlsafe(32)
    verification_tokens[token] = {
        'email': email,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=1),
        'verified': False
    }
    
    # In production, send email with verification link
    verification_link = f"http://localhost:5000/auth/verify?token={token}"
    
    return jsonify({
        'message': 'Verification email sent',
        'verification_link': verification_link  # For testing only
    }), 200

@bp.route('/verify', methods=['GET'])
def verify():
    """Verify email token and create session"""
    token = request.args.get('token', '')
    
    if not token or token not in verification_tokens:
        return render_template('verify_error.html', error='Invalid or expired token'), 400
    
    token_data = verification_tokens[token]
    
    # Check if token is expired
    if datetime.now() > token_data['expires_at']:
        del verification_tokens[token]
        return render_template('verify_error.html', error='Token has expired'), 400
    
    # Get or create user in database
    email = token_data['email']
    user_id = get_or_create_user(email)
    
    # Create session
    session.permanent = True
    session['user_email'] = email
    session['user_id'] = user_id
    session['verified_at'] = datetime.now().isoformat()
    
    # Clean up token
    del verification_tokens[token]
    
    return redirect(url_for('contract.generator'))

@bp.route('/logout', methods=['GET'])
def logout():
    """Clear user session"""
    session.clear()
    return redirect(url_for('auth.signin'))

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('auth.signin'))
        return f(*args, **kwargs)
    
    return decorated_function
