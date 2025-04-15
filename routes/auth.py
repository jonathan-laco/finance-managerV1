from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from services import user_service, category_service, config_service
from datetime import timedelta
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Verificar se o registro está habilitado
    registration_enabled = config_service.get_config('registration_enabled', True)
    if not registration_enabled:
        flash('O registro de novos usuários está desabilitado no momento.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name', '')
        
        # Verificar se o registro MEI está habilitado
        mei_registration_enabled = config_service.get_config('mei_registration_enabled', True)
        is_mei = False
        mei_cnpj = None
        mei_company_name = None

        if mei_registration_enabled and 'is_mei' in request.form:
            is_mei = True
            mei_cnpj = request.form.get('mei_cnpj', '')
            mei_company_name = request.form.get('mei_company_name', '')
            
            # Validar CNPJ se for MEI
            if not mei_cnpj:
                flash('CNPJ é obrigatório para MEI.', 'danger')
                return redirect(url_for('auth.register'))
        elif 'is_mei' in request.form and not mei_registration_enabled:
            # Se alguém tentar forçar o cadastro MEI quando desabilitado
            flash('O cadastro como MEI está desabilitado no momento.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verificar se requer aprovação do administrador
        require_approval = config_service.get_config('require_admin_approval', False)
        approval_status = 'pending' if require_approval else 'approved'
        is_active = not require_approval
        
        user, message = user_service.create_user(
            username, email, password, full_name, 
            is_mei=is_mei, mei_cnpj=mei_cnpj, mei_company_name=mei_company_name
        )
        
        if not user:
            flash(message, 'danger')
            return redirect(url_for('auth.register'))
        
        # Atualizar status de aprovação
        if require_approval:
            user.approval_status = 'pending'
            user.is_active = False
            db.session.commit()
        
        # Criar categorias padrão para o novo usuário
        category_service.create_default_categories(user.id)
        
        if require_approval:
            flash('Conta criada com sucesso! Aguarde a aprovação do administrador para acessar o sistema.', 'success')
        else:
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))
    
    # Verificar se o registro MEI está habilitado para exibir ou não a opção
    mei_registration_enabled = config_service.get_config('mei_registration_enabled', True)
    
    return render_template('register.html', mei_registration_enabled=mei_registration_enabled)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
      # Redirect admin users directly to admin dashboard
      if current_user.is_admin:
          return redirect(url_for('admin.dashboard'))
      return redirect(url_for('dashboard.index'))
      
  if request.method == 'POST':
      username = request.form.get('username')
      password = request.form.get('password')
      remember_me = 'remember' in request.form
      
      user = user_service.get_user_by_username(username)
      
      if not user or not user.check_password(password):
          flash('Verifique suas credenciais e tente novamente.', 'danger')
          return redirect(url_for('auth.login'))
      
      if not user.is_active:
          flash('Sua conta está desativada. Entre em contato com o administrador.', 'warning')
          return redirect(url_for('auth.login'))
      
      if user.approval_status == 'pending':
          flash('Sua conta está pendente de aprovação pelo administrador.', 'warning')
          return redirect(url_for('auth.login'))
      
      if user.approval_status == 'rejected':
          flash('Sua solicitação de cadastro foi rejeitada. Entre em contato com o administrador.', 'danger')
          return redirect(url_for('auth.login'))
      
      # Registrar o login do usuário
      user_service.log_user_login(user.id)
      
      # Se o usuário marcou "lembrar-me", definir a duração da sessão para 30 dias
      if remember_me:
          login_user(user, remember=True, duration=timedelta(days=30))
      else:
          login_user(user)
      
      # Redirecionar admin para dashboard administrativo
      if user.is_admin:
          return redirect(url_for('admin.dashboard'))
      
      # Verificar se há um próximo parâmetro para redirecionamento
      next_page = request.args.get('next')
      if next_page:
          return redirect(next_page)
          
      return redirect(url_for('dashboard.index'))
  
  # Verificar se há uma mensagem de erro de login
  error = request.args.get('error')
  if error and 'Please log in to access this page.' in error:
      flash('Por favor, faça login para acessar esta página.', 'danger')
  
  return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.index'))
