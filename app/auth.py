from flask import request, redirect, flash, Response, make_response
from flask_login import login_user, logout_user, current_user
from app import login_manager, bcrypt
from app.models.models import *
from .email import *


@login_manager.user_loader
def load_user(id):
    session = Session()
    user = session.query(User).filter(User.id == id).first()
    session.close()
    return user

#a
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.userTypeId == 1 and not current_user._mail_verified:  # Company Owner
            return render_template('email/not_verified.html', current_user=current_user, mail_verified="false")
        elif current_user.userTypeId == 3:  #admin
            return redirect('/admin')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('htmx/user/login.html', data={'return': '/login'})
    elif request.method == 'POST' and request.form:
        session = Session()
        email = request.form.get('email').lower()
        password = request.form.get('password')
        user = session.query(User).filter_by(email=email).first()
        session.close()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            response = Response()
            response.headers["hx-redirect"] = "/"
            return response
        else:
            flash("Email ou senha incorretos.", "error")
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
        try:
            send_confirmation(dict_data['email'])
        except:
            flash("Insira um email válido", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#signup_form .containerNotifications"
            return response
        dict_data['email'] = dict_data['email'].lower()

        session.add(user)
        session.commit()
        session.close()
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
