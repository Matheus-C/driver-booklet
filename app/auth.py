from flask import render_template,url_for,request,jsonify,send_file,redirect,flash
from app.models.models import *
from app.models.database import *
from app import app,login_manager,bcrypt
from flask_login import login_user,logout_user,current_user,login_required

@login_manager.user_loader
def load_user(id):
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    return user

@app.route('/')
def index():
    if current_user.is_authenticated:
        return str(current_user.name)
    else:
        return 'No user logged'

@app.route('/login',methods=['GET','POST'])
def login(id=None):
    if request.method == 'GET':
        return render_template('htmx/login.html')
    elif request.method == 'POST' and request.form:
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password=password)
        user = session.query(User).filter_by(email=email,password=hashed_password).first()
        login_user(user)
        return redirect('/')
    

@app.route('/signup',methods=['GET','POST'])
def signup(id=None):
    if request.method == 'GET':
        return render_template('htmx/signup.html')
    
    elif request.method == 'POST' and request.form:
        email = request.form.get('email')
        password = request.form.get('password')

        hashed_password = bcrypt.generate_password_hash(password=password)
        user = User(email=email,password=hashed_password)
        session = Session()
        user = session.add(user)
        session.commit()
        return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return 'Success'