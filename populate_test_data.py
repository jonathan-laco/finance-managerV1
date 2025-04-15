import sqlite3
import random
from datetime import datetime, timedelta
import os

# Configurações
DATABASE_PATH = 'finance.db'  # Caminho para o banco de dados SQLite
USER_ID = 1  # ID do usuário para o qual criar transações
NUM_TRANSACTIONS = 100  # Número de transações a serem criadas
START_DATE = datetime.now() - timedelta(days=180)  # Data de início (6 meses atrás)
END_DATE = datetime.now()  # Data de término (hoje)

# Verificar se o banco de dados existe
if not os.path.exists(DATABASE_PATH):
    print(f"Erro: Banco de dados '{DATABASE_PATH}' não encontrado.")
    exit(1)

# Conectar ao banco de dados
conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Verificar se o usuário existe
cursor.execute("SELECT id FROM user WHERE id = ?", (USER_ID,))
user = cursor.fetchone()
if not user:
    print(f"Erro: Usuário com ID {USER_ID} não encontrado.")
    exit(1)

# Obter contas do usuário
cursor.execute("SELECT id, name, balance FROM bank_account WHERE user_id = ?", (USER_ID,))
accounts = cursor.fetchall()
if not accounts:
    print(f"Erro: Nenhuma conta encontrada para o usuário {USER_ID}.")
    print("Por favor, crie pelo menos uma conta antes de executar este script.")
    exit(1)

# Obter categorias do usuário
cursor.execute("SELECT id, name, type FROM category WHERE user_id = ? AND is_active = 1", (USER_ID,))
categories = cursor.fetchall()
income_categories = [cat for cat in categories if cat['type'] == 'receita']
expense_categories = [cat for cat in categories if cat['type'] == 'despesa']

if not income_categories or not expense_categories:
    print(f"Erro: Categorias insuficientes para o usuário {USER_ID}.")
    print("Por favor, certifique-se de ter pelo menos uma categoria de receita e uma de despesa.")
    exit(1)

# Descrições de exemplo para transações
income_descriptions = [
    "Salário", "Freelance", "Dividendos", "Venda de item", "Reembolso", 
    "Bônus", "Presente", "Aluguel recebido", "Restituição de imposto", "Prêmio"
]

expense_descriptions = [
    "Supermercado", "Aluguel", "Conta de luz", "Conta de água", "Internet", 
    "Celular", "Transporte", "Restaurante", "Cinema", "Roupas", 
    "Farmácia", "Academia", "Assinatura streaming", "Material de escritório", "Manutenção do carro",
    "Combustível", "Presente para amigo", "Livros", "Curso online", "Viagem"
]

# Backup dos saldos originais das contas
account_original_balances = {account['id']: account['balance'] for account in accounts}

# Armazenar transações para inserção em lote
transactions_to_insert = []
account_balance_updates = {account['id']: 0 for account in accounts}

# Gerar transações aleatórias
print(f"Gerando {NUM_TRANSACTIONS} transações de teste...")

for _ in range(NUM_TRANSACTIONS):
    # Selecionar uma conta aleatória
    account = random.choice(accounts)
    account_id = account['id']
    
    # Determinar o tipo de transação (60% despesas, 40% receitas)
    transaction_type = 'despesa' if random.random() < 0.6 else 'receita'
    
    # Selecionar uma categoria apropriada
    if transaction_type == 'receita':
        category = random.choice(income_categories)
        description = random.choice(income_descriptions)
        # Valores de receita entre R$ 100 e R$ 5000
        amount = round(random.uniform(100, 5000), 2)
    else:
        category = random.choice(expense_categories)
        description = random.choice(expense_descriptions)
        # Valores de despesa entre R$ 10 e R$ 1000
        amount = round(random.uniform(10, 1000), 2)
    
    # Data aleatória dentro do intervalo
    days_range = (END_DATE - START_DATE).days
    random_days = random.randint(0, days_range)
    transaction_date = START_DATE + timedelta(days=random_days)
    
    # Status da transação (80% confirmadas, 15% pendentes, 5% canceladas)
    status_rand = random.random()
    if status_rand < 0.8:
        status = 'confirmado'
        is_confirmed = 1
    elif status_rand < 0.95:
        status = 'pendente'
        is_confirmed = 0
    else:
        status = 'cancelado'
        is_confirmed = 0
    
    # Adicionar à lista de transações para inserção
    transactions_to_insert.append((
        USER_ID,
        account_id,
        category['id'],
        transaction_type,
        amount,
        f"{description} {random.randint(1, 100)}",  # Adicionar número aleatório para variedade
        transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
        is_confirmed,
        status
    ))
    
    # Atualizar saldo da conta se a transação for confirmada
    if status == 'confirmado':
        if transaction_type == 'receita':
            account_balance_updates[account_id] += amount
        else:
            account_balance_updates[account_id] -= amount

# Inserir transações em lote
cursor.executemany(
    """
    INSERT INTO transaction 
    (user_id, account_id, category_id, type, amount, description, date, is_confirmed, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
    transactions_to_insert
)

# Atualizar saldos das contas
for account_id, balance_change in account_balance_updates.items():
    new_balance = account_original_balances[account_id] + balance_change
    cursor.execute(
        "UPDATE bank_account SET balance = ? WHERE id = ?",
        (new_balance, account_id)
    )

# Confirmar alterações
conn.commit()

# Resumo das transações criadas
cursor.execute("""
    SELECT type, status, COUNT(*) as count, SUM(amount) as total
    FROM transaction
    WHERE user_id = ? AND date >= ?
    GROUP BY type, status
""", (USER_ID, START_DATE.strftime('%Y-%m-%d %H:%M:%S')))

summary = cursor.fetchall()

print("\nResumo das transações criadas:")
print("-" * 50)
for row in summary:
    print(f"Tipo: {row['type']}, Status: {row['status']}")
    print(f"Quantidade: {row['count']}, Total: R$ {row['total']:.2f}")
    print("-" * 50)

# Resumo dos saldos atualizados
cursor.execute("SELECT id, name, balance FROM bank_account WHERE user_id = ?", (USER_ID,))
updated_accounts = cursor.fetchall()

print("\nSaldos atualizados das contas:")
print("-" * 50)
for account in updated_accounts:
    original_balance = account_original_balances[account['id']]
    print(f"Conta: {account['name']}")
    print(f"Saldo original: R$ {original_balance:.2f}")
    print(f"Saldo atual: R$ {account['balance']:.2f}")
    print(f"Variação: R$ {account['balance'] - original_balance:.2f}")
    print("-" * 50)

# Fechar conexão
conn.close()

print(f"\n{NUM_TRANSACTIONS} transações de teste foram criadas com sucesso!")
print("Você pode ajustar as configurações no início do script para gerar mais dados.")
