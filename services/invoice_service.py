from models import Invoice, Transaction
from extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def get_invoice_by_id(invoice_id, user_id):
    """
    Retorna uma nota fiscal específica de um usuário
    """
    return Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()

def get_invoice_by_transaction(transaction_id, user_id):
    """
    Retorna a nota fiscal associada a uma transação
    """
    return Invoice.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()

def create_invoice(user_id, transaction_id, file, invoice_number=None, invoice_date=None):
    """
    Cria uma nova nota fiscal
    """
    # Verificar se a transação existe e pertence ao usuário
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    if not transaction:
        return None, "Transação não encontrada"
    
    # Verificar se já existe uma nota fiscal para esta transação
    existing_invoice = get_invoice_by_transaction(transaction_id, user_id)
    if existing_invoice:
        return None, "Esta transação já possui uma nota fiscal"
    
    # Salvar o arquivo
    if file and file.filename:
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Criar diretório de uploads se não existir
        invoice_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'invoices', str(user_id))
        os.makedirs(invoice_upload_folder, exist_ok=True)
        
        # Caminho completo do arquivo
        file_path = os.path.join(invoice_upload_folder, unique_filename)
        
        # Salvar arquivo
        file.save(file_path)
        
        # Caminho relativo para armazenar no banco de dados
        relative_path = os.path.join('invoices', str(user_id), unique_filename)
        
        # Criar registro da nota fiscal
        new_invoice = Invoice(
            user_id=user_id,
            transaction_id=transaction_id,
            filename=unique_filename,
            original_filename=filename,
            file_path=relative_path,
            file_size=os.path.getsize(file_path),
            file_type=file.content_type,
            invoice_number=invoice_number,
            invoice_date=invoice_date
        )
        
        # Atualizar a transação para indicar que tem nota fiscal
        transaction.has_invoice = True
        
        db.session.add(new_invoice)
        db.session.commit()
        
        return new_invoice, "Nota fiscal adicionada com sucesso"
    
    return None, "Nenhum arquivo enviado"

def update_invoice(invoice_id, user_id, file=None, invoice_number=None, invoice_date=None):
    """
    Atualiza uma nota fiscal existente
    """
    invoice = get_invoice_by_id(invoice_id, user_id)
    if not invoice:
        return None, "Nota fiscal não encontrada"
    
    # Atualizar número e data da nota fiscal
    if invoice_number:
        invoice.invoice_number = invoice_number
    
    if invoice_date:
        invoice.invoice_date = invoice_date
    
    # Se um novo arquivo foi enviado, substituir o existente
    if file and file.filename:
        # Excluir arquivo antigo
        old_file_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], invoice.file_path)
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
        
        # Salvar novo arquivo
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Diretório de uploads
        invoice_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'invoices', str(user_id))
        os.makedirs(invoice_upload_folder, exist_ok=True)
        
        # Caminho completo do arquivo
        file_path = os.path.join(invoice_upload_folder, unique_filename)
        
        # Salvar arquivo
        file.save(file_path)
        
        # Caminho relativo para armazenar no banco de dados
        relative_path = os.path.join('invoices', str(user_id), unique_filename)
        
        # Atualizar registro da nota fiscal
        invoice.filename = unique_filename
        invoice.original_filename = filename
        invoice.file_path = relative_path
        invoice.file_size = os.path.getsize(file_path)
        invoice.file_type = file.content_type
    
    db.session.commit()
    
    return invoice, "Nota fiscal atualizada com sucesso"

def delete_invoice(invoice_id, user_id):
    """
    Exclui uma nota fiscal
    """
    invoice = get_invoice_by_id(invoice_id, user_id)
    if not invoice:
        return False, "Nota fiscal não encontrada"
    
    # Excluir arquivo
    file_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], invoice.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Atualizar a transação para indicar que não tem mais nota fiscal
    transaction = Transaction.query.get(invoice.transaction_id)
    if transaction:
        transaction.has_invoice = False
    
    # Excluir registro da nota fiscal
    db.session.delete(invoice)
    db.session.commit()
    
    return True, "Nota fiscal excluída com sucesso"

def get_user_invoices(user_id, limit=None):
    """
    Retorna todas as notas fiscais de um usuário
    """
    query = Invoice.query.filter_by(user_id=user_id).order_by(Invoice.uploaded_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()
