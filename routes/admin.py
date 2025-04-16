from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services import user_service, category_service, config_service
from models import User
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator para verificar se o usuário é administrador
def admin_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
      if not current_user.is_admin:
          flash('Acesso negado. Você precisa ser um administrador para acessar esta página.', 'danger')
          return redirect(url_for('dashboard.index'))
      return f(*args, **kwargs)
  return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
  # Obter estatísticas de usuários
  user_stats = user_service.get_user_statistics()
  
  return render_template('admin/dashboard.html', 
                        user_stats=user_stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
  # Obter todos os usuários
  users = user_service.get_all_users()
  
  return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
  success, message = user_service.toggle_user_status(user_id)
  
  if success:
      flash(message, 'success')
  else:
      flash(message, 'danger')
  
  return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
  new_password = request.form.get('new_password')
  
  if not new_password:
      flash('A nova senha não pode estar vazia', 'danger')
      return redirect(url_for('admin.users'))
  
  success, message = user_service.admin_change_user_password(user_id, new_password)
  
  if success:
      flash(message, 'success')
  else:
      flash(message, 'danger')
  
  return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
  email = request.form.get('email')
  full_name = request.form.get('full_name')
  
  user, message = user_service.update_user_profile(user_id, email, full_name)
  
  if not user:
      flash(message, 'danger')
  else:
      flash(message, 'success')
  
  return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/reset-data', methods=['POST'])
@login_required
@admin_required
def reset_user_data(user_id):
  success, message = user_service.reset_user_data(user_id)
  
  if success:
      # Recriar categorias padrão para o usuário
      category_service.create_default_categories(user_id)
      flash(message, 'success')
  else:
      flash(message, 'danger')
  
  return redirect(url_for('admin.users'))

@admin_bp.route('/access-logs')
@login_required
@admin_required
def access_logs():
    user_id = request.args.get('user_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Número de logs por página
    
    # Obter todos os usuários para exibir nomes na tabela
    users = User.query.all()
    
    if user_id:
        pagination = user_service.get_user_access_logs(user_id=user_id, page=page, per_page=per_page)
        user = user_service.get_user_by_id(user_id)
        return render_template('admin/access_logs.html', 
                              pagination=pagination, 
                              logs=pagination.items, 
                              filtered_user=user, 
                              users=users)
    else:
        pagination = user_service.get_user_access_logs(page=page, per_page=per_page)
        return render_template('admin/access_logs.html', 
                              pagination=pagination, 
                              logs=pagination.items, 
                              users=users)

@admin_bp.route('/config', methods=['GET', 'POST'])
@login_required
@admin_required
def system_config():
    if request.method == 'POST':
        # Atualizar configurações
        registration_enabled = 'registration_enabled' in request.form
        mei_registration_enabled = 'mei_registration_enabled' in request.form
        require_admin_approval = 'require_admin_approval' in request.form
        
        config_service.set_config('registration_enabled', registration_enabled)
        config_service.set_config('mei_registration_enabled', mei_registration_enabled)
        config_service.set_config('require_admin_approval', require_admin_approval)
        
        flash('Configurações atualizadas com sucesso', 'success')
        return redirect(url_for('admin.system_config'))
    
    # Obter configurações atuais
    configs = {
        'registration_enabled': config_service.get_config('registration_enabled', True),
        'mei_registration_enabled': config_service.get_config('mei_registration_enabled', True),
        'require_admin_approval': config_service.get_config('require_admin_approval', False)
    }
    
    return render_template('admin/system_config.html', configs=configs)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    success, message = user_service.delete_user(user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/pending-users')
@login_required
@admin_required
def pending_users():
    users = user_service.get_pending_users()
    return render_template('admin/pending_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_user(user_id):
    success, message = user_service.approve_user(user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.pending_users'))

@admin_bp.route('/users/<int:user_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_user(user_id):
    success, message = user_service.reject_user(user_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.pending_users'))
