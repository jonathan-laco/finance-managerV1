from models import User, UserAccessLog
from extensions import db
from utils.auth_helpers import custom_hash_password
from utils.file_helpers import save_picture
from werkzeug.security import check_password_hash
from datetime import datetime
from flask import request

def get_user_by_username(username):
    """
    Retorna um usuário pelo nome de usuário
    """
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """
    Retorna um usuário pelo email
    """
    return User.query.filter_by(email=email).first()

def get_user_by_id(user_id):
    """
    Retorna um usuário pelo ID
    """
    return User.query.get(user_id)

def get_all_users():
    """
    Retorna todos os usuários
    """
    return User.query.all()

def create_user(username, email, password, full_name='', is_admin=False, is_mei=False, mei_cnpj=None, mei_company_name=None):
    """
    Cria um novo usuário
    """
    # Verificar se o usuário ou email já existem
    user_exists = get_user_by_username(username)
    
    email_exists = get_user_by_email(email)
    
    if user_exists:
        return None, "Nome de usuário já existe"
    
    if email_exists:
        return None, "Email já está em uso"
    
    # Verificar se é o email de admin
    if email == 'admin@admin.com':
        is_admin = True
    
    # Criar novo usuário com hash personalizado
    hashed_password = custom_hash_password(password)
    new_user = User(
        username=username, 
        email=email, 
        password=hashed_password, 
        full_name=full_name,
        is_admin=is_admin,
        is_mei=is_mei,
        mei_cnpj=mei_cnpj,
        mei_company_name=mei_company_name
    )
    db.session.add(new_user)
    db.session.commit()
    
    return new_user, "Conta criada com sucesso"

def update_user_profile(user_id, email=None, full_name=None, profile_pic=None, is_mei=None, mei_cnpj=None, mei_company_name=None):
    """
    Atualiza o perfil de um usuário
    """
    user = User.query.get(user_id)
    if not user:
        return None, "Usuário não encontrado"
    
    if email:
        # Verificar se o email já está em uso por outro usuário
        email_exists = User.query.filter(User.email == email, User.id != user_id).first()
        if email_exists:
            return None, "Email já está em uso"
        user.email = email
    
    if full_name:
        user.full_name = full_name
    
    if profile_pic:
        try:
            picture_file = save_picture(profile_pic)
            user.profile_pic = picture_file
        except Exception as e:
            return None, f"Erro ao salvar imagem: {str(e)}"
    
    # Atualizar informações MEI
    if is_mei is not None:
        user.is_mei = is_mei
    
    if mei_cnpj:
        user.mei_cnpj = mei_cnpj
    
    if mei_company_name:
        user.mei_company_name = mei_company_name
    
    db.session.commit()
    return user, "Perfil atualizado com sucesso"

def change_user_password(user_id, current_password, new_password):
    """
    Altera a senha de um usuário
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    if not check_password_hash(user.password, current_password):
        return False, "Senha atual incorreta"
    
    user.password = custom_hash_password(new_password)
    db.session.commit()
    return True, "Senha alterada com sucesso"

def admin_change_user_password(user_id, new_password):
    """
    Altera a senha de um usuário (função de administrador)
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    user.password = custom_hash_password(new_password)
    db.session.commit()
    return True, "Senha alterada com sucesso"

def toggle_user_theme(user_id):
    """
    Alterna o tema do usuário entre claro e escuro
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    if user.theme == 'light':
        user.theme = 'dark'
    else:
        user.theme = 'light'
    
    db.session.commit()
    return True, "Tema alterado com sucesso"

def save_dashboard_layout(user_id, layout):
    """
    Salva o layout do dashboard do usuário
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    user.dashboard_layout = layout
    db.session.commit()
    return True, "Layout salvo com sucesso"

def log_user_login(user_id):
    """
    Registra o login do usuário
    """
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Atualizar o último login do usuário
    user.last_login = datetime.utcnow()
    
    # Criar um registro de acesso
    access_log = UserAccessLog(
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    
    db.session.add(access_log)
    db.session.commit()
    return True

def get_user_access_logs(user_id=None, limit=100):
    """
    Retorna os logs de acesso de um usuário ou de todos os usuários
    """
    if user_id:
        return UserAccessLog.query.filter_by(user_id=user_id).order_by(UserAccessLog.login_time.desc()).limit(limit).all()
    else:
        return UserAccessLog.query.order_by(UserAccessLog.login_time.desc()).limit(limit).all()

def toggle_user_status(user_id):
    """
    Ativa ou desativa um usuário
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    # Não permitir desativar o próprio administrador
    if user.is_admin and user.email == 'admin@admin.com':
        return False, "Não é possível desativar o administrador principal"
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "ativado" if user.is_active else "desativado"
    return True, f"Usuário {status} com sucesso"

def reset_user_data(user_id):
    """
    Reseta todos os dados de um usuário (transações, contas, categorias)
    """
    from models import Transaction, BankAccount, Category, Invoice
    
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    # Excluir todas as notas fiscais do usuário
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    for invoice in invoices:
        # Excluir arquivo
        from services.invoice_service import delete_invoice
        delete_invoice(invoice.id, user_id)
    
    # Excluir todas as transações do usuário
    Transaction.query.filter_by(user_id=user_id).delete()
    
    # Excluir todas as contas do usuário
    BankAccount.query.filter_by(user_id=user_id).delete()
    
    # Excluir todas as categorias do usuário
    Category.query.filter_by(user_id=user_id).delete()
    
    db.session.commit()
    return True, "Dados do usuário resetados com sucesso"

# Adicionar novas funções para gerenciar usuários

def delete_user(user_id):
    """
    Exclui um usuário e todos os seus dados
    """
    from models import User, Transaction, BankAccount, Category, Invoice, Goal, UserAccessLog
    
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    # Não permitir excluir o administrador principal
    if user.is_admin and user.email == 'admin@admin.com':
        return False, "Não é possível excluir o administrador principal"
    
    # Excluir todos os dados do usuário
    # Excluir todas as notas fiscais do usuário
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    for invoice in invoices:
        # Excluir arquivo
        from services.invoice_service import delete_invoice
        delete_invoice(invoice.id, user_id)
    
    # Excluir todas as transações do usuário
    Transaction.query.filter_by(user_id=user_id).delete()
    
    # Excluir todas as contas do usuário
    BankAccount.query.filter_by(user_id=user_id).delete()
    
    # Excluir todas as categorias do usuário
    Category.query.filter_by(user_id=user_id).delete()
    
    # Excluir todos os alertas do usuário
    Alert.query.filter_by(user_id=user_id).delete()
    
    # Excluir todas as metas do usuário
    Goal.query.filter_by(user_id=user_id).delete()
    
    # Excluir todos os logs de acesso do usuário
    UserAccessLog.query.filter_by(user_id=user_id).delete()
    
    # Finalmente, excluir o usuário
    db.session.delete(user)
    db.session.commit()
    
    return True, "Usuário excluído com sucesso"

def approve_user(user_id):
    """
    Aprova um usuário pendente
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    if user.approval_status != 'pending':
        return False, "Usuário não está pendente de aprovação"
    
    user.approval_status = 'approved'
    user.is_active = True
    db.session.commit()
    
    return True, "Usuário aprovado com sucesso"

def reject_user(user_id):
    """
    Rejeita um usuário pendente
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Usuário não encontrado"
    
    if user.approval_status != 'pending':
        return False, "Usuário não está pendente de aprovação"
    
    user.approval_status = 'rejected'
    user.is_active = False
    db.session.commit()
    
    return True, "Usuário rejeitado com sucesso"

def get_pending_users():
    """
    Retorna todos os usuários pendentes de aprovação
    """
    return User.query.filter_by(approval_status='pending').all()

def get_user_statistics():
    """
    Retorna estatísticas sobre os usuários
    """
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = User.query.filter_by(is_active=False).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    mei_users = User.query.filter_by(is_mei=True).count()
    pending_users = User.query.filter_by(approval_status='pending').count()
    
    # Usuários mais recentes
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Usuários com login mais recente
    recent_logins = User.query.filter(User.last_login != None).order_by(User.last_login.desc()).limit(5).all()
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_users': admin_users,
        'mei_users': mei_users,
        'pending_users': pending_users,
        'recent_users': recent_users,
        'recent_logins': recent_logins
    }
