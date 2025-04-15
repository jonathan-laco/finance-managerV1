from models import Goal
from extensions import db
from datetime import datetime
import pytz

def get_user_goals(user_id, status=None):
    """
    Retorna as metas de um usuário
    """
    query = Goal.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    return query.order_by(Goal.created_at.desc()).all()

def get_goal_by_id(goal_id, user_id):
    """
    Retorna uma meta específica de um usuário
    """
    return Goal.query.filter_by(id=goal_id, user_id=user_id).first()

def create_goal(user_id, title, description, target_amount, current_amount=0, target_date=None, category=None, color=None):
    """
    Cria uma nova meta
    """
    # Converter string para datetime se necessário
    if isinstance(target_date, str) and target_date:
        target_date = datetime.strptime(target_date, '%Y-%m-%d')
    
    new_goal = Goal(
        user_id=user_id,
        title=title,
        description=description,
        target_amount=target_amount,
        current_amount=current_amount,
        target_date=target_date,
        category=category,
        color=color or '#3498db'
    )
    
    db.session.add(new_goal)
    db.session.commit()
    
    return new_goal

def update_goal(goal_id, user_id, title=None, description=None, target_amount=None, 
               current_amount=None, target_date=None, category=None, color=None, status=None):
    """
    Atualiza uma meta existente
    """
    goal = get_goal_by_id(goal_id, user_id)
    if not goal:
        return None, "Meta não encontrada"
    
    if title:
        goal.title = title
    
    if description is not None:  # Permite descrição vazia
        goal.description = description
    
    if target_amount is not None:
        goal.target_amount = target_amount
    
    if current_amount is not None:
        goal.current_amount = current_amount
        
        # Se atingiu ou ultrapassou o valor alvo, marcar como concluída
        if goal.current_amount >= goal.target_amount and goal.status == 'in_progress':
            goal.status = 'completed'
    
    if target_date is not None:
        # Converter string para datetime se necessário
        if isinstance(target_date, str) and target_date:
            target_date = datetime.strptime(target_date, '%Y-%m-%d')
        goal.target_date = target_date
    
    if category:
        goal.category = category
    
    if color:
        goal.color = color
    
    if status:
        goal.status = status
    
    goal.updated_at = datetime.utcnow()
    db.session.commit()
    
    return goal, "Meta atualizada com sucesso"

def delete_goal(goal_id, user_id):
    """
    Exclui uma meta
    """
    goal = get_goal_by_id(goal_id, user_id)
    if not goal:
        return False, "Meta não encontrada"
    
    db.session.delete(goal)
    db.session.commit()
    
    return True, "Meta excluída com sucesso"

def add_to_goal(goal_id, user_id, amount):
    """
    Adiciona um valor a uma meta
    """
    goal = get_goal_by_id(goal_id, user_id)
    if not goal:
        return None, "Meta não encontrada"
    
    if goal.status != 'in_progress':
        return None, "Esta meta não está em andamento"
    
    goal.current_amount += amount
    
    # Se atingiu ou ultrapassou o valor alvo, marcar como concluída
    if goal.current_amount >= goal.target_amount:
        goal.status = 'completed'
    
    db.session.commit()
    
    return goal, "Valor adicionado com sucesso"

def get_goals_summary(user_id):
    """
    Retorna um resumo das metas do usuário
    """
    goals = get_user_goals(user_id)
    
    total_goals = len(goals)
    completed_goals = sum(1 for goal in goals if goal.status == 'completed')
    in_progress_goals = sum(1 for goal in goals if goal.status == 'in_progress')
    cancelled_goals = sum(1 for goal in goals if goal.status == 'cancelled')
    
    # Calcular o total de dinheiro necessário para completar todas as metas em andamento
    total_needed = sum(goal.target_amount - goal.current_amount for goal in goals if goal.status == 'in_progress')
    
    # Metas que estão próximas de serem concluídas (>= 90% completas)
    nearly_complete_goals = [goal for goal in goals if goal.status == 'in_progress' and goal.progress_percentage >= 90]
    
    # Metas que estão atrasadas (data limite próxima ou passada, mas progresso baixo)
    at_risk_goals = [goal for goal in goals if goal.status == 'in_progress' and goal.is_on_track == False]
    
    return {
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'in_progress_goals': in_progress_goals,
        'cancelled_goals': cancelled_goals,
        'total_needed': total_needed,
        'nearly_complete_goals': nearly_complete_goals,
        'at_risk_goals': at_risk_goals
    }
