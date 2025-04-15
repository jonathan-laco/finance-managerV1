from flask import Flask, render_template, redirect, url_for, flash, request, session, g
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os
import logging
from logging.handlers import RotatingFileHandler
import pytz
import requests

from config import Config
from extensions import db, login_manager
from models.user import User
from models.user_access_log import UserAccessLog
from utils.date_helpers import to_local_time, format_local_datetime, get_month_name, format_date, get_now_sp
from services import config_service

# Importar blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.accounts import accounts_bp
from routes.transactions import transactions_bp
from routes.categories import categories_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.admin import admin_bp
from routes.goals import goals_bp

def create_app(config_class=Config):
    # Inicialização da aplicação Flask
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Garantir que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensões
    db.init_app(app)
    login_manager.init_app(app)

    # Configurar mensagens de login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'danger'  # Categoria para mensagem em vermelho
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(goals_bp)
    
    # Configuração do carregador de usuário
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
        # Inicializar configurações padrão
        config_service.initialize_default_configs()
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/finance_manager.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Finance Manager startup')
    
    # Add template filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['get_month_name'] = get_month_name
    app.jinja_env.filters['format_local_datetime'] = format_local_datetime
    app.jinja_env.globals['to_local_time'] = to_local_time
    app.jinja_env.globals['get_now_sp'] = get_now_sp
    
    @app.before_request
    def before_request():
        g.user = current_user
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

# Criar a aplicação
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
