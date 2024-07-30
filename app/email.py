from flask import render_template, url_for
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from app import app
def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=43200):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail = Mail(app)
    mail.send(msg)


def send_confirmation(email):
    token = generate_confirmation_token(email)
    url = url_for('confirm_email', token=token, _external=True)
    msg = "Bem vindo ao Driver Booklet, Confirme seu email clicando no link abaixo:"
    html = render_template('email/email_template.html', url=url, msg=msg)
    subject = "Confirme seu email"
    send_email(email, subject, html)
