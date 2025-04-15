from models import Transaction, Category
from extensions import db
from datetime import datetime
from sqlalchemy import extract

def get_monthly_totals(user_id, month, year):
    """
    Calcula os totais de receitas e despesas de um mês específico
    """
    transactions = Transaction.query.filter_by(
        user_id=user_id,
        status='confirmado'
    ).filter(
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).all()
    
    total_income = sum(t.amount for t in transactions if t.type == 'receita')
    total_expense = sum(t.amount for t in transactions if t.type == 'despesa')
    
    return total_income, total_expense

def get_expense_categories_data(user_id, month, year):
    """
    Retorna dados de despesas por categoria para um mês específico
    """
    transactions = Transaction.query.filter_by(
        user_id=user_id,
        status='confirmado',
        type='despesa'
    ).filter(
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).all()
    
    expense_categories = {}
    expense_colors = {}
    
    for t in transactions:
        category = Category.query.get(t.category_id)
        if category:
            if category.name in expense_categories:
                expense_categories[category.name] += t.amount
            else:
                expense_categories[category.name] = t.amount
                expense_colors[category.name] = category.color
    
    return expense_categories, expense_colors

def get_daily_data(user_id, month, year):
    """
    Retorna dados diários de receitas e despesas para um mês específico
    """
    transactions = Transaction.query.filter_by(
        user_id=user_id,
        status='confirmado'
    ).filter(
        extract('month', Transaction.date) == month,
        extract('year', Transaction.date) == year
    ).all()
    
    daily_data = {}
    for t in transactions:
        day = t.date.day
        if day not in daily_data:
            daily_data[day] = {'receita': 0, 'despesa': 0}
        daily_data[day][t.type] += t.amount
    
    # Ordenar por dia
    daily_data = {k: daily_data[k] for k in sorted(daily_data.keys())}
    
    return daily_data

def get_monthly_data(user_id, current_month, current_year, num_months=6):
    """
    Retorna dados mensais de receitas e despesas para os últimos N meses
    """
    monthly_data = {}
    for i in range(num_months):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        month_trans = Transaction.query.filter_by(
            user_id=user_id,
            status='confirmado'
        ).filter(
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).all()
        
        month_income = sum(t.amount for t in month_trans if t.type == 'receita')
        month_expense = sum(t.amount for t in month_trans if t.type == 'despesa')
        
        month_name = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][month-1]
        monthly_data[f"{month_name}/{year}"] = {
            'receita': month_income,
            'despesa': month_expense,
            'saldo': month_income - month_expense
        }
    
    # Inverter para ordem cronológica
    monthly_data = {k: monthly_data[k] for k in reversed(list(monthly_data.keys()))}
    
    return monthly_data
