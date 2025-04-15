from extensions import db
from datetime import datetime

class UserAccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))  # IPv6 pode ter até 45 caracteres
    user_agent = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<UserAccessLog {self.user_id} at {self.login_time}>'
