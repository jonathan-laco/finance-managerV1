from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services import account_service

accounts_bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@accounts_bp.route('/')
@login_required
def index():
  # Redirecionar administradores
  if current_user.is_admin:
      flash('Administradores não possuem contas bancárias.', 'info')
      return redirect(url_for('admin.dashboard'))
      
  accounts = account_service.get_user_accounts(current_user.id)
  return render_template('bank_accounts.html', accounts=accounts)

@accounts_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        initial_balance = float(request.form.get('balance') or 0)
        
        account_service.create_account(current_user.id, name, initial_balance)
        
        flash('Conta adicionada com sucesso!', 'success')
        return redirect(url_for('accounts.index'))
    
    return render_template('add_account.html')

@accounts_bp.route('/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit(account_id):
    account = account_service.get_account_by_id(account_id, current_user.id)
    
    if not account:
        flash('Conta não encontrada!', 'danger')
        return redirect(url_for('accounts.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        account, message = account_service.update_account(account_id, current_user.id, name)
        
        if not account:
            flash(message, 'warning')
            return redirect(url_for('accounts.edit', account_id=account_id))
        
        flash(message, 'success')
        return redirect(url_for('accounts.index'))
    
    return render_template('edit_account.html', account=account)

@accounts_bp.route('/delete/<int:account_id>', methods=['POST'])
@login_required
def delete(account_id):
    success, message = account_service.delete_account(account_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('accounts.index'))
