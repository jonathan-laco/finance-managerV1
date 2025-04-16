from extensions import db
from datetime import datetime

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  
    original_filename = db.Column(db.String(255))  
    file_path = db.Column(db.String(255), nullable=False) 
    file_size = db.Column(db.Integer)  
    file_type = db.Column(db.String(50))  
    invoice_number = db.Column(db.String(50))  
    invoice_date = db.Column(db.DateTime)  
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com usuário e transação
    user = db.relationship('User', backref='invoices')
    transaction = db.relationship('Transaction', backref='invoice')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number} - {self.transaction_id}>'
