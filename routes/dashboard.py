from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
import json
from services import account_service, transaction_service, report_service, user_service
from utils.date_helpers import get_current_month, get_current_year

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Redirecionar administradores para o dashboard administrativo
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
        
    # Obter contas do usuário
    accounts = account_service.get_user_accounts(current_user.id)
    
    # Calcular saldo total
    total_balance = account_service.calculate_total_balance(current_user.id)
    
    # Obter transações recentes - usando get_user_transactions em vez de get_recent_transactions
    recent_transactions = transaction_service.get_user_transactions(
        current_user.id, 
        filters=None, 
        page=1, 
        per_page=5
    ).items
    
    # Calcular totais de receitas e despesas do mês atual
    current_month = get_current_month()
    current_year = get_current_year()
    
    total_income, total_expense = transaction_service.calculate_monthly_totals(
        current_user.id, current_month, current_year
    )
    
    # Dados para gráficos
    # Categorias de despesas para o gráfico de pizza
    expense_categories, expense_colors = report_service.get_expense_categories_data(
        current_user.id, current_month, current_year
    )
    
    # Dados para gráfico de linha (últimos 6 meses)
    monthly_data = report_service.get_monthly_data(
        current_user.id, current_month, current_year
    )
    
    # Transações pendentes
    pending_transactions = transaction_service.get_pending_transactions(current_user.id)
    
    # Obter layout do dashboard
    dashboard_layout = None
    if current_user.dashboard_layout:
        try:
            dashboard_layout = json.loads(current_user.dashboard_layout)
        except:
            dashboard_layout = None
    
    return render_template(
        'dashboard.html',
        accounts=accounts,
        total_balance=total_balance,
        recent_transactions=recent_transactions,
        total_income=total_income,
        total_expense=total_expense,
        expense_categories=expense_categories,
        expense_colors=expense_colors,
        monthly_data=monthly_data,
        pending_transactions=pending_transactions,
        dashboard_layout=dashboard_layout
    )

@dashboard_bp.route('/save-dashboard-layout', methods=['POST'])
@login_required
def save_layout():
    layout = request.json.get('layout')
    layout_json = json.dumps(layout)
    
    success, message = user_service.save_dashboard_layout(current_user.id, layout_json)
    
    return jsonify({'success': success})
