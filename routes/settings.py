from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services import user_service

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            email = request.form.get('email')
            full_name = request.form.get('full_name')
            
            # Processar foto de perfil, se enviada
            profile_pic = None
            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file.filename != '':
                    profile_pic = file
            
            user, message = user_service.update_user_profile(
                current_user.id, email, full_name, profile_pic
            )
            
            if not user:
                flash(message, 'danger')
            else:
                flash(message, 'success')
        
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password != confirm_password:
                flash('As novas senhas não coincidem!', 'danger')
            else:
                success, message = user_service.change_user_password(
                    current_user.id, current_password, new_password
                )
                
                if not success:
                    flash(message, 'danger')
                else:
                    flash(message, 'success')
    
    return render_template('config.html')

@settings_bp.route('/toggle-theme')
@login_required
def toggle_theme():
    success, _ = user_service.toggle_user_theme(current_user.id)
    return redirect(request.referrer or url_for('dashboard.index'))
