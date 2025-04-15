from models import Category, Transaction
from extensions import db

def get_user_categories(user_id, category_type=None, active_only=False):
    """
    Retorna as categorias de um usuário
    """
    query = Category.query.filter_by(user_id=user_id)
    
    if category_type:
        query = query.filter_by(type=category_type)
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    return query.order_by(Category.name).all()

def get_category_by_id(category_id, user_id):
    """
    Retorna uma categoria específica de um usuário
    """
    return Category.query.filter_by(id=category_id, user_id=user_id).first()

def create_category(user_id, name, category_type, color='#3c8dbc'):
    """
    Cria uma nova categoria
    """
    # Verificar se a categoria já existe para este usuário
    existing = Category.query.filter_by(user_id=user_id, name=name, type=category_type).first()
    if existing:
        return None, "Esta categoria já existe"
    
    new_category = Category(
        user_id=user_id,
        name=name,
        type=category_type,
        is_active=True,
        color=color
    )
    
    db.session.add(new_category)
    db.session.commit()
    return new_category, "Categoria adicionada com sucesso"

def update_category(category_id, user_id, name=None, color=None):
    """
    Atualiza uma categoria existente
    """
    category = get_category_by_id(category_id, user_id)
    if not category:
        return None, "Categoria não encontrada"
    
    if name:
        # Verificar se o novo nome já existe para outra categoria do mesmo tipo
        existing = Category.query.filter(
            Category.user_id == user_id,
            Category.name == name,
            Category.type == category.type,
            Category.id != category_id
        ).first()
        
        if existing:
            return None, "Já existe uma categoria com este nome"
        
        category.name = name
    
    if color:
        category.color = color
    
    db.session.commit()
    return category, "Categoria atualizada com sucesso"

def toggle_category_status(category_id, user_id):
    """
    Ativa ou desativa uma categoria
    """
    category = get_category_by_id(category_id, user_id)
    if not category:
        return None, "Categoria não encontrada"
    
    # Verificar se há transações usando esta categoria
    if not category.is_active:
        # Verificar se há transações pendentes usando esta categoria
        pending_transactions = Transaction.query.filter_by(
            category_id=category.id, 
            status='pendente'
        ).first()
        
        if pending_transactions:
            return None, "Não é possível ativar esta categoria pois existem transações pendentes associadas a ela"
    
    # Alternar status
    category.is_active = not category.is_active
    db.session.commit()
    
    status = 'ativada' if category.is_active else 'desativada'
    return category, f"Categoria {status} com sucesso"

def create_default_categories(user_id):
    """
    Cria categorias padrão para um novo usuário
    """
    default_income_categories = ['Salário', 'Investimentos', 'Freelance', 'Presente', 'Outros']
    default_expense_categories = ['Alimentação', 'Moradia', 'Transporte', 'Saúde', 'Educação', 'Lazer', 'Outros']
    
    for cat in default_income_categories:
        new_category = Category(name=cat, type='receita', user_id=user_id, is_active=True)
        db.session.add(new_category)
    
    for cat in default_expense_categories:
        new_category = Category(name=cat, type='despesa', user_id=user_id, is_active=True)
        db.session.add(new_category)
    
    db.session.commit()
