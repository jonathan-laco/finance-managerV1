from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services import goal_service
from datetime import datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goals_bp.route('/')
@login_required
def index():
    # Redirecionar administradores
    if current_user.is_admin:
        flash('Administradores não possuem metas.', 'info')
        return redirect(url_for('admin.dashboard'))
    
    # Obter todas as metas do usuário
    goals = goal_service.get_user_goals(current_user.id)
    
    # Obter resumo das metas
    summary = goal_service.get_goals_summary(current_user.id)
    
    # Separar metas por status
    in_progress_goals = [goal for goal in goals if goal.status == 'in_progress']
    completed_goals = [goal for goal in goals if goal.status == 'completed']
    cancelled_goals = [goal for goal in goals if goal.status == 'cancelled']
    
    return render_template(
        'goals/index.html',
        goals=goals,
        in_progress_goals=in_progress_goals,
        completed_goals=completed_goals,
        cancelled_goals=cancelled_goals,
        summary=summary
    )

@goals_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_amount = float(request.form.get('target_amount'))
        current_amount = float(request.form.get('current_amount', 0))
        target_date = request.form.get('target_date')
        category = request.form.get('category')
        color = request.form.get('color', '#3498db')
        
        goal = goal_service.create_goal(
            user_id=current_user.id,
            title=title,
            description=description,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            category=category,
            color=color
        )
        
        flash('Meta criada com sucesso!', 'success')
        return redirect(url_for('goals.index'))
    
    return render_template('goals/add.html')

@goals_bp.route('/edit/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def edit(goal_id):
    goal = goal_service.get_goal_by_id(goal_id, current_user.id)
    
    if not goal:
        flash('Meta não encontrada!', 'danger')
        return redirect(url_for('goals.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        target_amount = float(request.form.get('target_amount'))
        current_amount = float(request.form.get('current_amount', 0))
        target_date = request.form.get('target_date')
        category = request.form.get('category')
        color = request.form.get('color')
        status = request.form.get('status')
        
        goal, message = goal_service.update_goal(
            goal_id=goal_id,
            user_id=current_user.id,
            title=title,
            description=description,
            target_amount=target_amount,
            current_amount=current_amount,
            target_date=target_date,
            category=category,
            color=color,
            status=status
        )
        
        flash(message, 'success')
        return redirect(url_for('goals.index'))
    
    return render_template('goals/edit.html', goal=goal)

@goals_bp.route('/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete(goal_id):
    success, message = goal_service.delete_goal(goal_id, current_user.id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('goals.index'))

@goals_bp.route('/add_amount/<int:goal_id>', methods=['POST'])
@login_required
def add_amount(goal_id):
    amount = float(request.form.get('amount', 0))
    
    if amount <= 0:
        flash('O valor deve ser maior que zero!', 'danger')
        return redirect(url_for('goals.index'))
    
    goal, message = goal_service.add_to_goal(goal_id, current_user.id, amount)
    
    if goal:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('goals.index'))

@goals_bp.route('/details/<int:goal_id>')
@login_required
def details(goal_id):
    goal = goal_service.get_goal_by_id(goal_id, current_user.id)
    
    if not goal:
        flash('Meta não encontrada!', 'danger')
        return redirect(url_for('goals.index'))
    
    return render_template('goals/details.html', goal=goal)
