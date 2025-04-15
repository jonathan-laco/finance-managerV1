import os
import uuid
from flask import current_app

def save_picture(form_picture):
    """
    Salva uma imagem enviada pelo usuário com um nome único
    """
    random_hex = uuid.uuid4().hex
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn
