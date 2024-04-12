from flask import render_template,url_for,request,jsonify,send_file,redirect,flash
from app.models.models import *
from app.models.database import *
from app import app,login_manager
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

@app.route('/login',methods=['POST'])
def login(id):
    user = session.query(User).filter_by(id=id).first()
    login_user(user)
    return 'Success'

@app.route('/logout')
def logout():
    logout_user()
    return 'Success'