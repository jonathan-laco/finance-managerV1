from extensions import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_account.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    is_confirmed = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='confirmado')  # 'confirmado', 'pendente', 'cancelado'
    is_mei_transaction = db.Column(db.Boolean, default=False)  # Flag para transação MEI
    has_invoice = db.Column(db.Boolean, default=False)  # Flag para indicar se tem nota fiscal
    
    def __repr__(self):
        return f'<Transaction {self.description} ({self.amount})>'
