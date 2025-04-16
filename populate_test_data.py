import sqlite3
import random
from datetime import datetime, timedelta
import os

# Configurações
DATABASE_PATH = './instance/finance.db'  # Caminho para o banco de dados SQLite
USER_ID = 2  # ID do usuário para o qual criar transações
NUM_TRANSACTIONS = 50  # Número de transações a serem criadas
START_DATE = datetime(2025, 3, 1)  # Início de março de 2025
END_DATE = datetime(2025, 3, 31, 23, 59, 59)  # Fim de março de 2025

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
cursor.execute("SELECT id FROM bank_account WHERE user_id = ?", (USER_ID,))
accounts = cursor.fetchall()
if not accounts:
    print(f"Erro: Nenhuma conta encontrada para o usuário {USER_ID}.")
    exit(1)

# Obter categorias do usuário
cursor.execute("SELECT id, type FROM category WHERE user_id = ? AND is_active = 1", (USER_ID,))
categories = cursor.fetchall()
income_categories = [cat for cat in categories if cat['type'] == 'receita']
expense_categories = [cat for cat in categories if cat['type'] == 'despesa']

if not income_categories or not expense_categories:
    print(f"Erro: Categorias insuficientes para o usuário {USER_ID}.")
    exit(1)

# Descrições de exemplo para transações
income_descriptions = [
    "Salário", "Freelance", "Dividendos", "Venda de item", "Reembolso"
]
expense_descriptions = [
    "Supermercado", "Aluguel", "Conta de luz", "Internet", "Transporte"
]

# Gerar transações aleatórias
transactions_to_insert = []
for _ in range(NUM_TRANSACTIONS):
    # Selecionar uma conta aleatória
    account = random.choice(accounts)
    account_id = account['id']
    
    # Determinar o tipo de transação (50% despesas, 50% receitas)
    transaction_type = 'despesa' if random.random() < 0.5 else 'receita'
    
    # Selecionar uma categoria apropriada
    if transaction_type == 'receita':
        category = random.choice(income_categories)
        description = random.choice(income_descriptions)
        amount = round(random.uniform(100, 5000), 2)  # Valores de receita entre R$ 100 e R$ 5000
    else:
        category = random.choice(expense_categories)
        description = random.choice(expense_descriptions)
        amount = round(random.uniform(10, 1000), 2)  # Valores de despesa entre R$ 10 e R$ 1000
    
    # Data aleatória dentro de março de 2025
    days_range = (END_DATE - START_DATE).days
    random_days = random.randint(0, days_range)
    transaction_date = START_DATE + timedelta(days=random_days)
    
    # Status da transação (80% confirmadas, 20% pendentes)
    is_confirmed = 1 if random.random() < 0.8 else 0
    status = 'confirmado' if is_confirmed else 'pendente'
    
    # Adicionar à lista de transações para inserção
    transactions_to_insert.append((
        USER_ID,
        account_id,
        category['id'],
        transaction_type,
        amount,
        description,
        transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
        is_confirmed,
        status
    ))

# Inserir transações em lote
cursor.executemany(
    """
    INSERT INTO "transaction" 
    (user_id, account_id, category_id, type, amount, description, date, is_confirmed, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, 
    transactions_to_insert
)

# Confirmar alterações
conn.commit()

print(f"\n{NUM_TRANSACTIONS} transações de teste foram criadas com sucesso para março de 2025!")

# Fechar conexão
conn.close()
