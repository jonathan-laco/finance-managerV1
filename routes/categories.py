from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from services import category_service

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/')
@login_required
def index():
  # Redirecionar administradores
  if current_user.is_admin:
      flash('Administradores não possuem categorias.', 'info')
      return redirect(url_for('admin.dashboard'))
      
  income_categories = category_service.get_user_categories(current_user.id, 'receita')
  expense_categories = category_service.get_user_categories(current_user.id, 'despesa')
  
  return render_template('categories.html', 
                        income_categories=income_categories, 
                        expense_categories=expense_categories)

@categories_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    category_type = request.form.get('type')
    color = request.form.get('color', '#3c8dbc')
    
    category, message = category_service.create_category(
        current_user.id, name, category_type, color
    )
    
    if not category:
        flash(message, 'warning')
    else:
        flash(message, 'success')
    
    return redirect(url_for('categories.index'))

@categories_bp.route('/toggle/<int:category_id>')
@login_required
def toggle(category_id):
    category, message = category_service.toggle_category_status(category_id, current_user.id)
    
    if not category:
        flash(message, 'warning')
    else:
        flash(message, 'success')
    
    return redirect(url_for('categories.index'))

@categories_bp.route('/update/<int:category_id>', methods=['POST'])
@login_required
def update(category_id):
    name = request.form.get('name')
    color = request.form.get('color')
    
    category, message = category_service.update_category(
        category_id, current_user.id, name, color
    )
    
    if not category:
        flash(message, 'warning')
    else:
        flash(message, 'success')
    
    return redirect(url_for('categories.index'))
