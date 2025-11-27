from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file
from routes.auth_routes import require_auth
from models.contract import ContractData
from utils.contract_generator import ContractGenerator
from utils.file_utils import generate_filename
import os
from datetime import datetime

bp = Blueprint('contract', __name__, url_prefix='/contract')

@bp.route('/generator', methods=['GET'])
@require_auth
def generator():
    """Display contract generator form"""
    from utils.database import get_user_info
    
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    
    # Extract user name or use email
    user_name = user_info['name'] if user_info and user_info['name'] else user_info['email'].split('@')[0] if user_info else 'User'
    
    return render_template('contract_generator.html', user_name=user_name)

@bp.route('/generate', methods=['POST'])
@require_auth
def generate():
    """Process form submission and generate contract"""
    try:
        data = request.get_json()
        
        # Create contract data from form submission
        contract = ContractData.from_dict(data)
        
        # Validate contract data
        is_valid, errors = contract.validate()
        
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'errors': errors}), 400
        
        # Store contract data in session for preview/download
        session['contract_data'] = contract.to_json()
        session['contract_created_at'] = datetime.now().isoformat()
        
        return jsonify({
            'message': 'Contract generated successfully',
            'contract_id': session.get('contract_created_at')
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/preview', methods=['GET'])
@require_auth
def preview():
    """Display contract preview"""
    try:
        contract_json = session.get('contract_data')
        
        if not contract_json:
            return redirect(url_for('contract.generator'))
        
        contract = ContractData.from_json(contract_json)
        contract_html = ContractGenerator.format_contract_html(contract)
        
        return render_template('contract_preview.html', contract_html=contract_html)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/download/pdf', methods=['GET'])
@require_auth
def download_pdf():
    """Download contract as PDF"""
    try:
        contract_json = session.get('contract_data')
        
        if not contract_json:
            return jsonify({'error': 'No contract data found'}), 400
        
        contract = ContractData.from_json(contract_json)
        
        # Generate PDF
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        # Generate filename
        filename = generate_filename('pdf')
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/download/docx', methods=['GET'])
@require_auth
def download_docx():
    """Download contract as Word document"""
    try:
        contract_json = session.get('contract_data')
        
        if not contract_json:
            return jsonify({'error': 'No contract data found'}), 400
        
        contract = ContractData.from_json(contract_json)
        
        # Generate Word document
        docx_path = ContractGenerator.generate_docx(contract)
        
        # Generate filename
        filename = generate_filename('docx')
        
        return send_file(
            docx_path,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
