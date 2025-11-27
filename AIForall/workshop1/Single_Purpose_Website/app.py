from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_session import Session
import os
from datetime import datetime, timedelta
import secrets
import json

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize session
Session(app)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)

# Initialize database
from utils.database import init_db
init_db()

# Import routes - lazy import to avoid circular dependencies
def register_blueprints():
    from routes import auth_routes, contract_routes, contract_management_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(contract_routes.bp)
    app.register_blueprint(contract_management_routes.bp)

register_blueprints()


@app.route('/')
def index():
    """Home page - redirect to quick start if authenticated, else to signin"""
    if 'user_email' in session:
        return redirect(url_for('contracts_mgmt.quick_start'))
    return redirect(url_for('auth.signin'))

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
