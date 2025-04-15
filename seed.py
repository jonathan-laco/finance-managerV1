from models.user import User
from extensions import db
from services.user_service import create_user
from services.category_service import create_default_categories
from flask import current_app

def create_admin_user():
    """Cria o usuário administrador se ele não existir"""
    admin = User.query.filter_by(email='admin@admin.com').first()
    if not admin:
        print("Criando usuário administrador...")
        admin, _ = create_user(
            username='admin',
            email='admin@admin.com',
            password='admin123',
            full_name='Administrador',
            is_admin=True
        )
        
        # Criar categorias padrão para o admin
        if admin:
            create_default_categories(admin.id)
            print("Usuário administrador criado com sucesso!")
            return True
    return False

def run_seed():
    """Executa todas as funções de seed"""
    print("Iniciando seed do banco de dados...")
    
    try:
        # Criar usuário administrador
        admin_created = create_admin_user()
        
        # Commit das alterações
        db.session.commit()
        
        if admin_created:
            print("Seed concluído com sucesso!")
        else:
            print("Seed concluído. Nenhuma alteração necessária.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro durante o seed: {e}")
        raise

if __name__ == "__main__":
    # Este bloco permite executar o seed diretamente
    from app import app
    with app.app_context():
        run_seed()
