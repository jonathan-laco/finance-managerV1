from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from services import transaction_service, account_service, category_service, report_service
from utils.date_helpers import get_current_month, get_current_year

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    # Redirecionar administradores
    if current_user.is_admin:
        flash('Administradores não possuem relatórios financeiros.', 'info')
        return redirect(url_for('admin.dashboard'))
    
    # Se o usuário for MEI, redirecionar para o relatório MEI
    if current_user.is_mei:
        return redirect(url_for('reports.mei_report'))
    
    # Verificar se é relatório mensal ou anual
    period = request.args.get('period', 'month')
    
    # Filtros comuns
    year = request.args.get('year', type=int, default=get_current_year())
    month = request.args.get('month', type=int, default=get_current_month())
    
    # Inicializar variáveis para relatório anual
    annual_income = 0
    annual_expense = 0
    annual_data = []
    
    # Se for relatório anual, calcular dados para o ano inteiro
    if period == 'year':
        month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # Calcular dados para cada mês do ano
        for month_num in range(1, 13):
            # Filtros para o mês específico
            month_filters = {
                'month': month_num,
                'year': year
            }
            
            # Calcular totais para o mês
            month_income, month_expense = report_service.get_monthly_totals(
                current_user.id, month_num, year
            )
            
            # Adicionar ao total anual
            annual_income += month_income
            annual_expense += month_expense
            
            # Adicionar dados do mês para o gráfico/tabela
            annual_data.append({
                'month': month_num,
                'month_name': month_names[month_num-1],
                'income': month_income,
                'expense': month_expense
            })
        
        # Contar transações do ano
        year_filters = {
            'year': year
        }
        
        total_transactions_month = transaction_service.count_filtered_transactions(
            current_user.id, year_filters
        )
        
        # Usar os totais anuais para o relatório
        total_income = annual_income
        total_expense = annual_expense
        
        # Obter contas e categorias para os filtros
        accounts = account_service.get_user_accounts(current_user.id)
        categories = category_service.get_user_categories(current_user.id, active_only=True)
        
        # Data atual para o relatório
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Contar total de transações
        total_all_transactions = transaction_service.count_all_user_transactions(current_user.id)
        
        return render_template(
            'reports.html',
            total_income=total_income,
            total_expense=total_expense,
            accounts=accounts,
            categories=categories,
            current_month=month,
            current_year=year,
            current_date=current_date,
            total_transactions_month=total_transactions_month,
            total_all_transactions=total_all_transactions,
            annual_income=annual_income,
            annual_expense=annual_expense,
            annual_data=annual_data,
            period=period
        )
    else:
        # Relatório mensal (código existente)
        account_id = request.args.get('account', type=int)
        transaction_type = request.args.get('type')
        category_id = request.args.get('category', type=int)
        
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Montar filtros
        filters = {
            'month': month,
            'year': year
        }
        
        if account_id:
            filters['account_id'] = account_id
        if transaction_type:
            filters['type'] = transaction_type
        if category_id:
            filters['category_id'] = category_id
        
        # Obter transações paginadas para exibição na tela
        paginated_transactions = transaction_service.get_user_transactions(
            current_user.id, filters, page, per_page
        )
        
        # Obter todas as transações para impressão (sem paginação)
        all_transactions = transaction_service.get_all_user_transactions(
            current_user.id, filters
        )
        
        # Contar transações
        total_transactions_month = transaction_service.count_filtered_transactions(
            current_user.id, filters
        )
        
        total_all_transactions = transaction_service.count_all_user_transactions(
            current_user.id
        )
        
        # Calcular totais
        total_income, total_expense = report_service.get_monthly_totals(
            current_user.id, month, year
        )
        
        # Dados para gráficos
        # Categorias de despesas para o gráfico de pizza
        expense_categories, expense_colors = report_service.get_expense_categories_data(
            current_user.id, month, year
        )
        
        # Dados para gráfico de linha (receitas e despesas por dia)
        daily_data = report_service.get_daily_data(
            current_user.id, month, year
        )
        
        # Dados para gráfico de barras (últimos 6 meses)
        monthly_data = report_service.get_monthly_data(
            current_user.id, month, year
        )
        
        # Obter contas e categorias para os filtros
        accounts = account_service.get_user_accounts(current_user.id)
        categories = category_service.get_user_categories(current_user.id, active_only=True)
        
        # Data atual para o relatório
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return render_template(
            'reports.html',
            transactions=paginated_transactions.items,
            all_transactions=all_transactions,
            pagination=paginated_transactions,
            total_income=total_income,
            total_expense=total_expense,
            expense_categories=expense_categories,
            expense_colors=expense_colors,
            daily_data=daily_data,
            monthly_data=monthly_data,
            current_month=month,
            current_year=year,
            accounts=accounts,
            categories=categories,
            current_date=current_date,
            total_transactions_month=total_transactions_month,
            total_all_transactions=total_all_transactions,
            period=period
        )

@reports_bp.route('/transactions')
@login_required
def transactions_report():
    # Filtros
    month = request.args.get('month', type=int, default=get_current_month())
    year = request.args.get('year', type=int, default=get_current_year())
    account_id = request.args.get('account', type=int)
    transaction_type = request.args.get('type')
    category_id = request.args.get('category', type=int)
    
    # Verificar se é relatório mensal ou anual
    period = request.args.get('period', 'month')
    
    # Inicializar variáveis para relatório anual
    annual_income = 0
    annual_expense = 0
    annual_data = []
    
    # Se for relatório anual, calcular dados para o ano inteiro
    if period == 'year':
        month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # Calcular dados para cada mês do ano
        for month_num in range(1, 13):
            # Filtros para o mês específico
            month_filters = {
                'month': month_num,
                'year': year
            }
            
            # Calcular totais para o mês
            month_income, month_expense = report_service.get_monthly_totals(
                current_user.id, month_num, year
            )
            
            # Adicionar ao total anual
            annual_income += month_income
            annual_expense += month_expense
            
            # Adicionar dados do mês para o gráfico/tabela
            annual_data.append({
                'month': month_num,
                'month_name': month_names[month_num-1],
                'income': month_income,
                'expense': month_expense
            })
        
        # Contar transações do ano
        year_filters = {
            'year': year
        }
        
        total_transactions_month = transaction_service.count_filtered_transactions(
            current_user.id, year_filters
        )
        
        # Usar os totais anuais para o relatório
        total_income = annual_income
        total_expense = annual_expense
        
        # Obter contas e categorias para os filtros
        accounts = account_service.get_user_accounts(current_user.id)
        categories = category_service.get_user_categories(current_user.id, active_only=True)
        
        # Data atual para o relatório
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Contar total de transações
        total_all_transactions = transaction_service.count_all_user_transactions(current_user.id)
        
        return render_template(
            'transactions_report.html',
            total_income=total_income,
            total_expense=total_expense,
            accounts=accounts,
            categories=categories,
            current_month=month,
            current_year=year,
            current_date=current_date,
            total_transactions_month=total_transactions_month,
            total_all_transactions=total_all_transactions,
            annual_income=annual_income,
            annual_expense=annual_expense,
            annual_data=annual_data,
            period=period
        )
    else:
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Montar filtros
        filters = {
            'month': month,
            'year': year
        }
        
        if account_id:
            filters['account_id'] = account_id
        if transaction_type:
            filters['type'] = transaction_type
        if category_id:
            filters['category_id'] = category_id
        
        # Obter transações paginadas para exibição na tela
        paginated_transactions = transaction_service.get_user_transactions(
            current_user.id, filters, page, per_page
        )
        
        # Obter todas as transações para impressão (sem paginação)
        all_transactions = transaction_service.get_all_user_transactions(
            current_user.id, filters
        )
        
        # Contar transações
        total_transactions_month = transaction_service.count_filtered_transactions(
            current_user.id, filters
        )
        
        total_all_transactions = transaction_service.count_all_user_transactions(
            current_user.id
        )
        
        # Calcular totais
        total_income, total_expense = report_service.get_monthly_totals(
            current_user.id, month, year
        )
        
        # Obter contas e categorias para os filtros
        accounts = account_service.get_user_accounts(current_user.id)
        categories = category_service.get_user_categories(current_user.id, active_only=True)
        
        # Data atual para o relatório
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return render_template(
            'transactions_report.html',
            transactions=paginated_transactions.items,
            all_transactions=all_transactions,
            pagination=paginated_transactions,
            total_income=total_income,
            total_expense=total_expense,
            accounts=accounts,
            categories=categories,
            current_month=month,
            current_year=year,
            current_date=current_date,
            total_transactions_month=total_transactions_month,
            total_all_transactions=total_all_transactions,
            period=period
        )

@reports_bp.route('/mei')
@login_required
def mei_report():
    # Verificar se o usuário é MEI
    if not current_user.is_mei:
        flash('Você não está registrado como MEI.', 'warning')
        return redirect(url_for('reports.index'))
        
    # Verificar se é relatório mensal ou anual
    period = request.args.get('period', 'month')
    
    # Filtros comuns
    year = request.args.get('year', type=int, default=get_current_year())
    month = request.args.get('month', type=int, default=get_current_month())
    
    # Inicializar variáveis para relatório anual
    annual_income = 0
    annual_expense = 0
    annual_data = []
    
    # Se for relatório anual, calcular dados para o ano inteiro
    if period == 'year':
        month_names = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        # Calcular dados para cada mês do ano
        for month_num in range(1, 13):
            # Filtros para o mês específico
            month_filters = {
                'month': month_num,
                'year': year,
                'is_mei_transaction': True
            }
            
            # Calcular totais para o mês
            month_income, month_expense = transaction_service.calculate_monthly_totals(
                current_user.id, month_num, year, is_mei_only=True
            )
            
            # Adicionar ao total anual
            annual_income += month_income
            annual_expense += month_expense
            
            # Adicionar dados do mês para o gráfico/tabela
            annual_data.append({
                'month': month_num,
                'month_name': month_names[month_num-1],
                'income': month_income,
                'expense': month_expense
            })
        
        # Contar transações do ano
        year_filters = {
            'year': year,
            'is_mei_transaction': True
        }
        
        total_transactions_month = transaction_service.count_filtered_transactions(
            current_user.id, year_filters
        )
        
        # Usar os totais anuais para o relatório
        total_income = annual_income
        total_expense = annual_expense
        
        # Obter contas e categorias para os filtros
        accounts = account_service.get_user_accounts(current_user.id)
        categories = category_service.get_user_categories(current_user.id, active_only=True)
        
        # Data atual para o relatório
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # Contar total de transações
        total_all_transactions = transaction_service.count_all_user_transactions(
            current_user.id
        )
        
        return render_template(
            'mei_report.html',
            total_income=total_income,
            total_expense=total_expense,
            accounts=accounts,
            categories=categories,
            current_month=month,
            current_year=year,
            current_date=current_date,
            total_transactions_month=total_transactions_month,
            total_all_transactions=total_all_transactions,
            annual_income=annual_income,
            annual_expense=annual_expense,
            annual_data=annual_data,
            period=period
        )
    else:
        # Relatório mensal (código existente)
        account_id = request.args.get('account', type=int)
        transaction_type = request.args.get('type')
        category_id = request.args.get('category', type=int)
        has_invoice = request.args.get('has_invoice', type=int)
        
        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Montar filtros
        filters = {
            'month': month,
            'year': year,
            'is_mei_transaction': True
        }
        
        if account_id:
            filters['account_id'] = account_id
        if transaction_type:
            filters['type'] = transaction_type
        if category_id:
            filters['category_id'] = category_id
        if has_invoice is not None:
            filters['has_invoice'] = bool(has_invoice)
        
        # Obter transações paginadas para exibição na tela
        paginated_transactions = transaction_service.get_user_transactions(
            current_user.id, filters, page, per_page
        )
        
        # Obter todas as transações para impressão (sem paginação)
        all_transactions = transaction_service.get_all_user_transactions(
            current_user.id, filters
        )
        
        # Contar transações
        total_transactions_month = transaction_service.count_filtered_transactions(
            current_user.id, filters
        )
        
        # Calcular totais mensais
        total_income, total_expense = transaction_service.calculate_monthly_totals(
            current_user.id, month, year, is_mei_only=True
        )
        
        # Calcular faturamento anual total (para alerta de limite MEI)
        # Usamos apenas as receitas para verificar o limite MEI
        year_income_filters = {
            'year': year,
            'is_mei_transaction': True,
            'type': 'receita'
        }
        
        # Obter todas as transações de receita do ano
        year_income_transactions = transaction_service.get_all_user_transactions(
            current_user.id, year_income_filters
        )
        
        # Calcular o total de receitas do ano
        annual_income = sum(transaction.amount for transaction in year_income_transactions)
        
        # Contar total de transações (independente do período)
        total_all_transactions = transaction_service.count_all_user_transactions(
            current_user.id
        )
        
        # Obter contas e categorias para os filtros
        accounts = account_service.get_user_accounts(current_user.id)
        categories = category_service.get_user_categories(current_user.id, active_only=True)
        
        # Data atual para o relatório
        current_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        return render_template(
            'mei_report.html',
            transactions=paginated_transactions.items,
            all_transactions=all_transactions,
            pagination=paginated_transactions,
            total_income=total_income,
            total_expense=total_expense,
            accounts=accounts,
            categories=categories,
            current_month=month,
            current_year=year,
            current_date=current_date,
            total_transactions_month=total_transactions_month,
            total_all_transactions=total_all_transactions,
            annual_income=annual_income,
            period=period
        )
