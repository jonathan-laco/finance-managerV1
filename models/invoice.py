from extensions import db
from datetime import datetime

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Nome do arquivo salvo
    original_filename = db.Column(db.String(255))  # Nome original do arquivo
    file_path = db.Column(db.String(255), nullable=False)  # Caminho relativo do arquivo
    file_size = db.Column(db.Integer)  # Tamanho do arquivo em bytes
    file_type = db.Column(db.String(50))  # Tipo MIME do arquivo
    invoice_number = db.Column(db.String(50))  # Número da nota fiscal
    invoice_date = db.Column(db.DateTime)  # Data da nota fiscal
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com usuário e transação
    user = db.relationship('User', backref='invoices')
    transaction = db.relationship('Transaction', backref='invoice')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.transaction_id}>'
