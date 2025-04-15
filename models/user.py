from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200), default='default_profile.png')
    theme = db.Column(db.String(10), default='light')  # 'light' ou 'dark'
    dashboard_layout = db.Column(db.Text)  # JSON para armazenar layout do dashboard
    is_admin = db.Column(db.Boolean, default=False)  # Flag para administrador
    is_active = db.Column(db.Boolean, default=True)  # Flag para conta ativa/inativa
    approval_status = db.Column(db.String(20), default='approved')  # 'pending', 'approved', 'rejected'
    is_mei = db.Column(db.Boolean, default=False)  # Flag para MEI
    mei_cnpj = db.Column(db.String(18))  # CNPJ do MEI
    mei_company_name = db.Column(db.String(100))  # Nome da empresa MEI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    accounts = db.relationship('BankAccount', backref='owner', lazy=True)
    transactions = db.relationship('Transaction', backref='owner', lazy=True)
    categories = db.relationship('Category', backref='owner', lazy=True)
    access_logs = db.relationship('UserAccessLog', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
