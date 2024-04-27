from flask import render_template,url_for,request,jsonify,send_file,redirect,flash, Response
from app.models.models import *
from app.models.database import *
from app import app,login_manager,bcrypt
from flask_login import login_user,logout_user,current_user,login_required

@login_manager.user_loader
def load_user(id):
    session = Session()
    user = session.query(User).filter(User.id==id).first()
    session.close()
    return user

@app.route('/')
def index():
    if current_user.is_authenticated:
        print('this route')
        return render_template('index.html', current_user=current_user)
    else:
        return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login(id=None):
    if request.method == 'GET':
        return render_template('htmx/login.html', data={'return':'/login'})
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
            return render_template('htmx/login.html', data={'return':'/login'}, current_user = current_user)


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'GET':
        return render_template('htmx/signup.html',data={'return':'/signup'}, current_user = current_user)
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        session = Session()
        if(session.query(User).filter(User.email==dict_data['email']).first() != None or\
            session.query(User).filter(User.userIdentification==dict_data['userIdentification']).first()):
            flash("User already registered.", "error")
            return render_template('htmx/signup.html',data={'return':'/signup'}, current_user = current_user)

        
        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password'])
        dict_data['userTypeId'] = 1 #Owner
        # dict_data['is_active'] = 0 #Has to be enabled manually
        
        user = User(**dict_data)
        
        user = session.add(user)
        session.commit()
        session.close()
        flash("Registered successfully.", "success")
        return render_template('htmx/signup.html',data={'return':'/signup'}, current_user = current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')