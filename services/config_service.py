from models.system_config import SystemConfig
from extensions import db

def get_config(key, default=None):
    """
    Obtém uma configuração do sistema pelo nome
    """
    config = SystemConfig.query.filter_by(key=key).first()
    if config:
        # Converter para boolean se for 'true' ou 'false'
        if config.value.lower() == 'true':
            return True
        elif config.value.lower() == 'false':
            return False
        # Converter para int se for número
        elif config.value.isdigit():
            return int(config.value)
        return config.value
    return default

def set_config(key, value, description=None):
    """
    Define uma configuração do sistema
    """
    # Converter boolean para string
    if isinstance(value, bool):
        value = str(value).lower()
    elif isinstance(value, (int, float)):
        value = str(value)
    
    config = SystemConfig.query.filter_by(key=key).first()
    if config:
        config.value = value
        if description:
            config.description = description
    else:
        config = SystemConfig(key=key, value=value, description=description)
        db.session.add(config)
    
    db.session.commit()
    return config

def get_all_configs():
    """
    Retorna todas as configurações do sistema
    """
    return SystemConfig.query.all()

def initialize_default_configs():
    """
    Inicializa as configurações padrão do sistema
    """
    default_configs = {
        'registration_enabled': ('true', 'Permite que novos usuários se registrem no sistema'),
        'mei_registration_enabled': ('true', 'Permite que usuários se registrem como MEI'),
        'require_admin_approval': ('false', 'Requer aprovação do administrador para novos cadastros'),
    }
    
    for key, (value, description) in default_configs.items():
        if not SystemConfig.query.filter_by(key=key).first():
            set_config(key, value, description)
