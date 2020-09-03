import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flaskblog import mail  
from flask import current_app

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,'static/profile_pic',picture_file_name)

    output_size = (140,140)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    #i.save(picture_path)
    
    i.save(picture_path)

    return picture_file_name


def send_reset_email(user):
    token = User.get_reset_token(user)
    msg = Message('Password Reset Request',sender='',recipients=[user.email])

    msg.body = f'''To reset your Password,visit the following link:
{url_for('users.reset_token',token=token,_external=True)}
If you did not make the request please IGNORE the email and no changes will be made
    '''
    mail.send(msg)
