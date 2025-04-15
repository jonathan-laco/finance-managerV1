from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, send_file
from flask_login import login_required, current_user
from services import transaction_service, account_service, category_service, invoice_service
from datetime import datetime
import os
from flask import current_app
from utils.date_helpers import get_now_sp, format_date

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/')
@login_required
def index():
    # Redirecionar administradores
    if current_user.is_admin:
        flash('Administradores não possuem transações.', 'info')
        return redirect(url_for('admin.dashboard'))
        
    # Filtros
    account_id = request.args.get('account', type=int)
    transaction_type = request.args.get('type')
    status = request.args.get('status')
    category_id = request.args.get('category', type=int)
    has_invoice = request.args.get('has_invoice', type=int)

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Montar filtros
    filters = {}
    if account_id:
        filters['account_id'] = account_id
    if transaction_type:
        filters['type'] = transaction_type
    if status:
        filters['status'] = status
    if category_id:
        filters['category_id'] = category_id
    if has_invoice is not None:
        filters['has_invoice'] = bool(has_invoice)
    
    # Se o usuário for MEI, filtrar apenas transações MEI
    if current_user.is_mei:
        filters['is_mei_transaction'] = True

    # Obter transações paginadas
    paginated_transactions = transaction_service.get_user_transactions(
        current_user.id, filters, page, per_page
    )

    # Obter contas para o filtro
    accounts = account_service.get_user_accounts(current_user.id)

    # Obter categorias para o filtro
    categories = category_service.get_user_categories(current_user.id, active_only=True)

    # Obter data atual correta usando o helper
    current_date = get_now_sp()

    # Se o usuário for MEI, usar o template de transações MEI
    if current_user.is_mei:
        return render_template('mei_transactions.html', 
                            transactions=paginated_transactions.items, 
                            pagination=paginated_transactions,
                            accounts=accounts, 
                            categories=categories,
                            current_month=current_date.month,
                            current_year=current_date.year,
                            current_date=current_date)
    else:
        return render_template('transactions.html', 
                            transactions=paginated_transactions.items, 
                            pagination=paginated_transactions,
                            accounts=accounts, 
                            categories=categories,
                            is_mei=False,
                            current_date=current_date)

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        account_id = request.form.get('account_id', type=int)
        transaction_type = request.form.get('type')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        category_id = request.form.get('category_id', type=int)
        is_confirmed = 'is_confirmed' in request.form
        
        # Se o usuário for MEI, todas as transações são automaticamente MEI
        is_mei_transaction = current_user.is_mei
        
        # Usar a data atual correta
        current_date = get_now_sp()
        
        transaction, message = transaction_service.create_transaction(
            current_user.id, account_id, category_id, transaction_type, 
            amount, description, is_confirmed, is_mei_transaction, current_date
        )
        
        if not transaction:
            flash(message, 'danger')
            return redirect(url_for('transactions.add'))
        
        # Verificar se há nota fiscal para upload (apenas para MEI)
        if current_user.is_mei and 'invoice_file' in request.files and request.files['invoice_file'].filename:
            invoice_file = request.files['invoice_file']
            invoice_number = request.form.get('invoice_number')
            invoice_date_str = request.form.get('invoice_date')
            
            # Converter data da nota fiscal
            invoice_date = None
            if invoice_date_str:
                try:
                    invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d')
                except ValueError:
                    pass
            
            # Criar nota fiscal
            invoice, invoice_message = invoice_service.create_invoice(
                current_user.id, transaction.id, invoice_file, invoice_number, invoice_date
            )
            
            if not invoice:
                flash(invoice_message, 'warning')
            else:
                flash(invoice_message, 'success')
        
        flash(message, 'success')
        return redirect(url_for('transactions.index'))

    # Obter contas do usuário para o formulário
    accounts = account_service.get_user_accounts(current_user.id)

    # Obter categorias ativas do usuário
    income_categories = category_service.get_user_categories(current_user.id, 'receita', True)
    expense_categories = category_service.get_user_categories(current_user.id, 'despesa', True)

    # Obter data atual correta
    current_date = get_now_sp()

    return render_template(
        'add_transaction.html',
        accounts=accounts,
        income_categories=income_categories,
        expense_categories=expense_categories,
        is_mei=current_user.is_mei,
        current_date=current_date
    )

@transactions_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit(transaction_id):
    # Buscar a transação
    transaction = transaction_service.get_transaction_by_id(transaction_id, current_user.id)

    if not transaction:
        flash('Transação não encontrada!', 'danger')
        return redirect(url_for('transactions.index'))

    # Obter contas do usuário para o formulário
    accounts = account_service.get_user_accounts(current_user.id)

    # Obter categorias ativas do usuário
    income_categories = category_service.get_user_categories(current_user.id, 'receita', True)
    expense_categories = category_service.get_user_categories(current_user.id, 'despesa', True)

    # Obter nota fiscal associada, se houver
    invoice = None
    if transaction.has_invoice:
        invoice = invoice_service.get_invoice_by_transaction(transaction.id, current_user.id)

    # Obter data atual correta
    current_date = get_now_sp()

    if request.method == 'POST':
        try:
            account_id = request.form.get('account_id', type=int)
            transaction_type = request.form.get('type')
            amount = float(request.form.get('amount'))
            description = request.form.get('description')
            category_id = request.form.get('category_id', type=int)
            is_confirmed = 'is_confirmed' in request.form
            
            # Se o usuário for MEI, a transação é automaticamente MEI
            is_mei_transaction = current_user.is_mei
            
            # Atualizar a transação
            updated_transaction, message = transaction_service.update_transaction(
                transaction_id, current_user.id, account_id, category_id, 
                transaction_type, amount, description, is_confirmed, is_mei_transaction
            )
            
            if not updated_transaction:
                flash(message, 'danger')
                return redirect(url_for('transactions.edit', transaction_id=transaction_id))
            
            # Verificar se há nota fiscal para upload (apenas para MEI)
            if current_user.is_mei and 'invoice_file' in request.files and request.files['invoice_file'].filename:
                invoice_file = request.files['invoice_file']
                invoice_number = request.form.get('invoice_number')
                invoice_date_str = request.form.get('invoice_date')
                
                # Converter data da nota fiscal
                invoice_date = None
                if invoice_date_str:
                    try:
                        invoice_date = datetime.strptime(invoice_date_str, '%Y-%m-%d')
                    except ValueError:
                        pass
                
                # Se já existe uma nota fiscal, atualizar
                if invoice:
                    invoice, invoice_message = invoice_service.update_invoice(
                        invoice.id, current_user.id, invoice_file, invoice_number, invoice_date
                    )
                else:
                    # Criar nova nota fiscal
                    invoice, invoice_message = invoice_service.create_invoice(
                        current_user.id, transaction.id, invoice_file, invoice_number, invoice_date
                    )
                
                if not invoice:
                    flash(invoice_message, 'warning')
                else:
                    flash(invoice_message, 'success')
            
            flash(message, 'success')
            return redirect(url_for('transactions.index'))
            
        except Exception as e:
            current_app.logger.error(f"Erro ao editar transação: {str(e)}")
            flash(f"Erro ao editar transação: {str(e)}", 'danger')
            return redirect(url_for('transactions.edit', transaction_id=transaction_id))

    return render_template(
        'edit_transaction.html',
        transaction=transaction,
        accounts=accounts,
        income_categories=income_categories,
        expense_categories=expense_categories,
        invoice=invoice,
        is_mei=current_user.is_mei,
        current_date=current_date
    )

@transactions_bp.route('/delete/<int:transaction_id>', methods=['POST'])
@login_required
def delete(transaction_id):
    success, message = transaction_service.delete_transaction(transaction_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(request.referrer or url_for('transactions.index'))

@transactions_bp.route('/confirm/<int:transaction_id>')
@login_required
def confirm(transaction_id):
    success, message = transaction_service.confirm_transaction(transaction_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(request.referrer or url_for('transactions.index'))

@transactions_bp.route('/cancel/<int:transaction_id>')
@login_required
def cancel(transaction_id):
    success, message = transaction_service.cancel_transaction(transaction_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(request.referrer or url_for('transactions.index'))

@transactions_bp.route('/download-invoice/<int:transaction_id>')
@login_required
def download_invoice(transaction_id):
    try:
        # Verificar se a transação existe e pertence ao usuário
        transaction = transaction_service.get_transaction_by_id(transaction_id, current_user.id)
        if not transaction or not transaction.has_invoice:
            flash('Nota fiscal não encontrada!', 'danger')
            return redirect(url_for('transactions.index'))
        
        # Obter a nota fiscal
        invoice = invoice_service.get_invoice_by_transaction(transaction_id, current_user.id)
        if not invoice:
            flash('Nota fiscal não encontrada!', 'danger')
            return redirect(url_for('transactions.index'))
        
        # Diretório de uploads
        upload_dir = os.path.dirname(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], invoice.file_path))
        filename = os.path.basename(invoice.file_path)
        
        # Retornar o arquivo
        return send_from_directory(
            upload_dir,
            filename,
            as_attachment=True,
            download_name=invoice.original_filename
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao baixar nota fiscal: {str(e)}")
        flash(f"Erro ao baixar nota fiscal: {str(e)}", 'danger')
        return redirect(url_for('transactions.index'))

@transactions_bp.route('/delete-invoice/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def delete_invoice(transaction_id):
    # Verificar se a transação existe e pertence ao usuário
    transaction = transaction_service.get_transaction_by_id(transaction_id, current_user.id)
    if not transaction or not transaction.has_invoice:
        flash('Nota fiscal não encontrada!', 'danger')
        return redirect(url_for('transactions.index'))
    
    # Obter a nota fiscal
    invoice = invoice_service.get_invoice_by_transaction(transaction_id, current_user.id)
    if not invoice:
        flash('Nota fiscal não encontrada!', 'danger')
        return redirect(url_for('transactions.index'))
    
    # Excluir a nota fiscal
    success, message = invoice_service.delete_invoice(invoice.id, current_user.id)
    
    if success:
        # Atualizar o status da transação para indicar que não tem mais nota fiscal
        from extensions import db
        transaction.has_invoice = False
        db.session.commit()
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('transactions.edit', transaction_id=transaction_id))
