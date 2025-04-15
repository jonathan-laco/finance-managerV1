from extensions import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'receita' ou 'despesa'
    is_active = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(20), default='#3c8dbc')
    transactions = db.relationship('Transaction', backref='category_rel', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'
