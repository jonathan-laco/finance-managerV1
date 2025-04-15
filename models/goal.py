from extensions import db
from datetime import datetime
import pytz

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    
    # Valores da meta
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    
    # Data limite para atingir a meta
    target_date = db.Column(db.DateTime, nullable=True)
    
    # Categoria da meta (ex: 'casa', 'carro', 'viagem', 'educação', etc.)
    category = db.Column(db.String(50))
    
    # Cor para representação visual
    color = db.Column(db.String(20), default='#3498db')
    
    # Status: 'in_progress', 'completed', 'cancelled'
    status = db.Column(db.String(20), default='in_progress')
    
    # Data de criação e última atualização
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Goal {self.title} - {self.target_amount}>'
    
    @property
    def progress_percentage(self):
        """Calcula a porcentagem de progresso da meta"""
        if self.target_amount <= 0:
            return 0
        
        percentage = (self.current_amount / self.target_amount) * 100
        return min(100, percentage)  # Limita a 100% mesmo se o valor atual exceder o alvo
    
    @property
    def days_remaining(self):
        """Calcula quantos dias restam até a data alvo"""
        if not self.target_date:
            return None
        
        sp_tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(pytz.utc)
        
        # Se o datetime não tem informação de timezone, assume que é UTC
        target_date_utc = self.target_date
        if target_date_utc.tzinfo is None:
            target_date_utc = pytz.utc.localize(target_date_utc)
        
        delta = target_date_utc - now
        return max(0, delta.days)  # Retorna 0 se já passou da data
    
    @property
    def is_on_track(self):
        """Verifica se a meta está no caminho certo para ser atingida no prazo"""
        if not self.target_date or self.status != 'in_progress':
            return None
        
        # Se já atingiu a meta, está no caminho certo
        if self.current_amount >= self.target_amount:
            return True
        
        # Se não tem dias restantes, não está no caminho certo
        if self.days_remaining == 0:
            return False
        
        # Calcula quanto deveria ter sido economizado até agora
        sp_tz = pytz.timezone('America/Sao_Paulo')
        now = datetime.now(pytz.utc)
        
        # Se o datetime não tem informação de timezone, assume que é UTC
        target_date_utc = self.target_date
        if target_date_utc.tzinfo is None:
            target_date_utc = pytz.utc.localize(target_date_utc)
            
        created_at_utc = self.created_at
        if created_at_utc.tzinfo is None:
            created_at_utc = pytz.utc.localize(created_at_utc)
        
        total_days = (target_date_utc - created_at_utc).days
        days_passed = (now - created_at_utc).days
        
        if total_days <= 0:
            return False
        
        expected_progress = (days_passed / total_days) * self.target_amount
        return self.current_amount >= expected_progress
