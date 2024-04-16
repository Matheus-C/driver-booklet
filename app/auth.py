from flask import render_template,url_for,request,jsonify,send_file,redirect,flash
from app.models.models import *
from app.models.database import *
from app import app,login_manager,bcrypt
from flask_login import login_user,logout_user,current_user,login_required

@login_manager.user_loader
def load_user(id):
    session = Session()
    user = session.query(User).filter_by(id=id).first()
    session.close()
    return user

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user=current_user)
    else:
        return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login(id=None):
    if request.method == 'GET':
        return render_template('htmx/login.html')
    elif request.method == 'POST' and request.form:
        email = request.form.get('email')
        password = request.form.get('password')
        user = session.query(User).filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user)
            return redirect('/')
        else:
            return redirect('/login')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('htmx/signup.html',data={'return':'/signup'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password'])
        dict_data['userTypeId'] = 1 #Owner
        dict_data['is_active'] = 0 #Has to be enabled manually
        
        user = User(**dict_data)
        session = Session()
        user = session.add(user)
        session.commit()
        session.close()

        return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')