from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from routes.auth_routes import require_auth
from models.contract import ContractData
from utils.database import (
    save_contract, update_contract, get_contract, get_user_contracts,
    delete_contract, get_user_by_email
)
import json

bp = Blueprint('contracts_mgmt', __name__, url_prefix='/contracts')

@bp.route('/quick-start', methods=['GET'])
@require_auth
def quick_start():
    """Display quick start page for returning users"""
    from utils.database import get_user_info, get_user_drafts
    
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    contracts = get_user_contracts(user_id)
    drafts = get_user_drafts(user_id)
    
    # Extract user name or use email
    user_name = user_info['name'] if user_info and user_info['name'] else user_info['email'].split('@')[0] if user_info else 'User'
    
    return render_template('quick_start.html',
        user_name=user_name,
        total_contracts=len(contracts),
        total_drafts=len(drafts),
        recent_contracts=contracts,
        recent_drafts=drafts)

@bp.route('/list', methods=['GET'])
@require_auth
def list_contracts():
    """Display list of user's contracts"""
    from utils.database import get_user_info, get_user_drafts
    
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    contracts = get_user_contracts(user_id)
    drafts = get_user_drafts(user_id)
    
    # Extract user name or use email
    user_name = user_info['name'] if user_info and user_info['name'] else user_info['email'].split('@')[0] if user_info else 'User'
    user_email = user_info['email'] if user_info else session.get('user_email')
    
    # Check if user is returning (has contracts)
    is_returning_user = len(contracts) > 0 or len(drafts) > 0
    
    return render_template('contracts_list.html', 
        contracts=contracts, 
        drafts=drafts,
        user_name=user_name,
        user_email=user_email,
        is_returning_user=is_returning_user)

@bp.route('/new', methods=['GET'])
@require_auth
def new_contract():
    """Start a new contract"""
    return redirect(url_for('contract.generator'))

@bp.route('/save', methods=['POST'])
@require_auth
def save_new_contract():
    """Save a new contract"""
    try:
        from utils.database import save_draft
        
        user_id = session.get('user_id')
        data = request.get_json()
        
        title = data.get('title', 'Untitled Contract')
        contract_data = data.get('contract_data')
        save_as_draft = data.get('save_as_draft', False)
        
        if not contract_data:
            return jsonify({'error': 'No contract data provided'}), 400
        
        # Save to database
        if save_as_draft:
            contract_id = save_draft(user_id, title, contract_data)
            message = 'Contract saved as draft'
        else:
            contract_id = save_contract(user_id, title, contract_data)
            message = 'Contract saved successfully'
        
        return jsonify({
            'message': message,
            'contract_id': contract_id,
            'is_draft': save_as_draft
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:contract_id>/view', methods=['GET'])
@require_auth
def view_contract(contract_id):
    """View a saved contract"""
    try:
        contract = get_contract(contract_id)
        
        if not contract:
            return render_template('error.html', error='Contract not found'), 404
        
        # Format contract for display
        from utils.contract_generator import ContractGenerator
        contract_html = ContractGenerator.format_contract_html(
            ContractData.from_dict(contract['data'])
        )
        
        return render_template('contract_view.html',
            contract=contract,
            contract_html=contract_html
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:contract_id>/edit', methods=['GET'])
@require_auth
def edit_contract(contract_id):
    """Edit a saved contract"""
    try:
        contract = get_contract(contract_id)
        
        if not contract:
            return render_template('error.html', error='Contract not found'), 404
        
        # Store contract data in session for editing
        session['contract_data'] = json.dumps(contract['data'])
        session['contract_id'] = contract_id
        session['contract_title'] = contract['title']
        
        return render_template('contract_generator.html',
            edit_mode=True,
            contract_id=contract_id,
            contract_data=contract['data']
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:contract_id>/update', methods=['POST'])
@require_auth
def update_saved_contract(contract_id):
    """Update an existing contract"""
    try:
        data = request.get_json()
        
        title = data.get('title', 'Untitled Contract')
        contract_data = data.get('contract_data')
        
        if not contract_data:
            return jsonify({'error': 'No contract data provided'}), 400
        
        # Update in database
        update_contract(contract_id, title, contract_data)
        
        return jsonify({
            'message': 'Contract updated successfully',
            'contract_id': contract_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:contract_id>/delete', methods=['POST'])
@require_auth
def delete_saved_contract(contract_id):
    """Delete a contract"""
    try:
        delete_contract(contract_id)
        
        return jsonify({
            'message': 'Contract deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:contract_id>/download/pdf', methods=['GET'])
@require_auth
def download_contract_pdf(contract_id):
    """Download a saved contract as PDF"""
    try:
        from utils.contract_generator import ContractGenerator
        from utils.file_utils import generate_filename
        from flask import send_file
        
        contract = get_contract(contract_id)
        
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404
        
        # Generate PDF
        contract_obj = ContractData.from_dict(contract['data'])
        pdf_path = ContractGenerator.generate_pdf(contract_obj)
        
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

@bp.route('/<int:contract_id>/download/docx', methods=['GET'])
@require_auth
def download_contract_docx(contract_id):
    """Download a saved contract as Word document"""
    try:
        from utils.contract_generator import ContractGenerator
        from utils.file_utils import generate_filename
        from flask import send_file
        
        contract = get_contract(contract_id)
        
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404
        
        # Generate Word document
        contract_obj = ContractData.from_dict(contract['data'])
        docx_path = ContractGenerator.generate_docx(contract_obj)
        
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

@bp.route('/<int:contract_id>/duplicate', methods=['POST'])
@require_auth
def duplicate_contract(contract_id):
    """Duplicate an existing contract as a new draft"""
    try:
        from utils.database import save_draft
        
        user_id = session.get('user_id')
        contract = get_contract(contract_id)
        
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404
        
        # Create new title with "Copy" suffix
        new_title = f"{contract['title']} (Copy)"
        
        # Save as draft
        new_contract_id = save_draft(user_id, new_title, contract['data'])
        
        return jsonify({
            'message': 'Contract duplicated successfully',
            'contract_id': new_contract_id,
            'redirect_url': url_for('contracts_mgmt.edit_contract', contract_id=new_contract_id)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:contract_id>/use-as-template', methods=['POST'])
@require_auth
def use_as_template(contract_id):
    """Use an existing contract as a template for a new one"""
    try:
        from utils.database import save_draft
        
        user_id = session.get('user_id')
        contract = get_contract(contract_id)
        
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404
        
        # Create new title with "Template" suffix
        new_title = f"{contract['title']} - New"
        
        # Save as draft
        new_contract_id = save_draft(user_id, new_title, contract['data'])
        
        # Store in session for editing
        session['contract_data'] = json.dumps(contract['data'])
        session['contract_id'] = new_contract_id
        session['contract_title'] = new_title
        
        return jsonify({
            'message': 'Template loaded successfully',
            'contract_id': new_contract_id,
            'redirect_url': url_for('contracts_mgmt.edit_contract', contract_id=new_contract_id)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
