from werkzeug.security import generate_password_hash

def custom_hash_password(password):
    """
    Função personalizada para hash de senha
    """
    return generate_password_hash(password)
