from flask import render_template, url_for, request, redirect, flash, Response, make_response
from flask_login import login_user, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from app import app, login_manager, bcrypt
from app.models.models import *


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


@login_manager.user_loader
def load_user(id):
    session = Session()
    user = session.query(User).filter(User.id == id).first()
    session.close()
    return user


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.userTypeId == 1:  # Company Owner
            if current_user._mail_verified:
                return redirect('/companies')
            else:
                return render_template('email/not_verified.html', current_user=current_user, mail_verified="false")
        elif current_user.userTypeId == 2:  #worker
            return redirect('/timer')
        elif current_user.userTypeId == 3:  #admin
            return redirect('/admin')
    else:
        return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login(id=None):
    if request.method == 'GET':
        return render_template('htmx/user/login.html', data={'return': '/login'})
    elif request.method == 'POST' and request.form:
        session = Session()
        email = request.form.get('email')
        password = request.form.get('password')
        user = session.query(User).filter_by(email=email).first()
        session.close()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            response = Response()
            response.headers["hx-redirect"] = "/"
            return response
        else:
            flash("Wrong email or password.", "error")
            return render_template('base/notifications.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('htmx/user/signup.html', data={'return': '/signup', 'target': '#signup_form'},
                               current_user=current_user)

    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        session = Session()
        if (session.query(User).filter(User.email == dict_data['email']).first() is not None or
                session.query(User).filter(User.userIdentification == dict_data['userIdentification']).first()):
            flash("Email ou NIF já registrado.", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#signup_form .containerNotifications"
            return response

        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password']).decode('utf-8')
        dict_data['userTypeId'] = "1"  #Owner
        # noinspection PyArgumentList
        user = User(**dict_data)

        session.add(user)
        session.commit()
        session.close()
        send_confirmation(dict_data['email'])
        flash('Uma confirmação foi enviada para o seu email.', 'success')
        return render_template('email/notice_email.html', current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
        if not email:
            raise Exception
    except:
        flash('O link de confirmação é inválido ou expirou.', 'error')
        return render_template('index.html')
    session = Session()
    user = session.query(User).filter(User.email == email).first()
    if user._mail_verified:
        flash('Email já confirmado. Por favor faça o login', 'success')
    else:
        user._mail_verified = True
        session.add(user)
        session.commit()
        session.close()
        flash('Email confirmado com sucesso.', 'success')
    return render_template("confirmation.html", current_user=current_user)


@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgot_password.html', data={'return': '/forgot'})
    elif request.method == 'POST':
        dict_data = request.form.to_dict()
        session = Session()
        if session.query(User).filter(User.email == dict_data['email']).first() is None:
            flash("O Email não existe no nosso banco de dados.", "error")
            return render_template('base/notifications.html')
        else:
            token = generate_confirmation_token(dict_data['email'])
            url = url_for('new_password', token=token, _external=True)
            msg = "Clique no link abaixo para redefinir sua senha:"
            html = render_template('email/email_template.html', url=url, msg=msg)
            subject = "Redefinição de senha"
            send_email(dict_data['email'], subject, html)
            flash("Foi enviado um Email contendo um link para a redefinição da senha.", "success")
            return render_template('base/notifications.html')


@app.route('/password/<token>', methods=['GET', 'POST'])
def new_password(token):
    try:
        email = confirm_token(token)
        if not email:
            raise Exception
    except:
        flash('O link de troca de senha é inválido ou expirou.', 'error')
        return render_template('index.html')
    if request.method == 'GET':
        return render_template('new_password.html', data={'return': f'/password/{token}'})
    elif request.method == 'POST':
        dict_data = request.form.to_dict()
        if dict_data['password'] != dict_data['confirm']:
            flash("A senha e a confirmação não são idênticas", "error")
            return render_template('base/notifications.html')
        session = Session()
        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password']).decode('utf-8')
        user = session.query(User).filter(User.email == email).first()
        user.password = dict_data['password']
        session.add(user)
        session.commit()
        session.close()
        flash('Senha alterada com sucesso.', 'success')
        response = Response()
        response.headers["hx-redirect"] = "/"
        return response


@app.route('/resend/confirmation')
def resend_confirmation():
    if current_user.is_authenticated:
        send_confirmation(current_user.email)
        flash('Uma confirmação foi enviada para o seu email.', 'success')
        return render_template('base/notifications.html')
