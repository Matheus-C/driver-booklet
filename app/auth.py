from flask import render_template,url_for,request,jsonify,send_file,redirect,flash, Response
from app.models.models import *
from app.models.database import *
from app import app,login_manager,bcrypt
from flask_login import login_user,logout_user,current_user,login_required
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
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

@login_manager.user_loader
def load_user(id):
    session = Session()
    user = session.query(User).filter(User.id==id).first()
    session.close()
    return user

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.userTypeId == 1: # Company Owner
            return redirect('/companies')
        else: #Other
            return redirect('/timer')
    else:
        return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login(id=None):
    if request.method == 'GET':
        return render_template('htmx/user/login.html', data={'return':'/login'})
    elif request.method == 'POST' and request.form:
        session = Session()
        email = request.form.get('email')
        password = request.form.get('password')
        user = session.query(User).filter_by(email=email).first()
        session.close()
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user,remember=True)
            response = Response()
            response.headers["hx-redirect"] = "/"
            return response
        else:
            flash("Wrong email or password.", "error")
            return render_template('htmx/user/login.html', data={'return':'/login'}, current_user = current_user)


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('htmx/user/signup.html',data={'return':'/signup'}, current_user = current_user)
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        session = Session()
        if(session.query(User).filter(User.email==dict_data['email']).first() != None or\
            session.query(User).filter(User.userIdentification==dict_data['userIdentification']).first()):
            flash("User already registered.", "error")
            return render_template('htmx/user/signup.html',data={'return':'/signup'}, current_user = current_user)

        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password']).decode('utf-8')
        dict_data['userTypeId'] = 1 #Owner
        user = User(**dict_data)
        
        session.add(user)
        session.commit()
        token = generate_confirmation_token(dict_data['email'])
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('confirmation_email.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(dict_data['email'], subject, html)
        session.refresh(user)
        login_user(user)
        session.close()
        flash('A confirmation email has been sent via email.', 'success')
        return render_template('notice_email.html', current_user = current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    session = Session()
    user = session.query(User).filter(User.email==email).first()
    if user.is_active:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.is_active = True
        session.add(user)
        session.commit()
        session.close()
        flash('You have confirmed your account. Thanks!', 'success')
    return render_template("confirmation.html", current_user = current_user)