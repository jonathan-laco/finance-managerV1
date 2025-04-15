from models import BankAccount, Transaction
from extensions import db
from flask import flash

def get_user_accounts(user_id):
    """
    Retorna todas as contas de um usuário
    """
    return BankAccount.query.filter_by(user_id=user_id).all()

def get_account_by_id(account_id, user_id):
    """
    Retorna uma conta específica de um usuário
    """
    return BankAccount.query.filter_by(id=account_id, user_id=user_id).first()

def create_account(user_id, name, initial_balance=0.0):
    """
    Cria uma nova conta bancária
    """
    new_account = BankAccount(
        user_id=user_id,
        name=name,
        balance=initial_balance
    )
    db.session.add(new_account)
    db.session.commit()
    return new_account

def update_account(account_id, user_id, name):
    """
    Atualiza os dados de uma conta bancária
    """
    account = get_account_by_id(account_id, user_id)
    if not account:
        return None, "Conta não encontrada"
    
    # Verificar se o nome já existe para outra conta do mesmo usuário
    existing = BankAccount.query.filter(
        BankAccount.user_id == user_id,
        BankAccount.name == name,
        BankAccount.id != account_id
    ).first()
    
    if existing:
        return None, "Já existe uma conta com este nome"
    
    account.name = name
    db.session.commit()
    return account, "Conta atualizada com sucesso"

def delete_account(account_id, user_id):
    """
    Exclui uma conta bancária se não houver transações associadas
    """
    account = get_account_by_id(account_id, user_id)
    if not account:
        return False, "Conta não encontrada"
    
    # Verificar se existem transações associadas a esta conta
    transactions = Transaction.query.filter_by(account_id=account_id).first()
    if transactions:
        return False, "Não é possível excluir esta conta pois existem transações associadas a ela"
    
    db.session.delete(account)
    db.session.commit()
    return True, "Conta excluída com sucesso"

def calculate_total_balance(user_id):
    """
    Calcula o saldo total de todas as contas do usuário
    """
    accounts = get_user_accounts(user_id)
    return sum(account.balance for account in accounts)
