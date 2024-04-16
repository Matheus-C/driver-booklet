from flask import render_template, request, url_for, redirect
from app.models.models import *
from app.models.database import *
from app import app,bcrypt
from flask_login import current_user,login_required


@app.route("/company", methods=["GET","POST"])
@login_required
def company():
    if current_user:
        
        if request.method == 'GET':
            return render_template('htmx/company_add_form.html',current_user=current_user)
        
        elif request.method == 'POST' and request.form:
            dict_data = request.form.to_dict()
            dict_data['idUser'] = current_user.id
            company = Company(**dict_data)
            session = Session()
            session.add(company)
            session.commit()
            session.close()
            return url_for('/profile')
        
@app.route("/company/<id>", methods=["GET","POST"])
@login_required
def company_info(id):
    if current_user:
        
        if request.method == 'GET':
            session = Session()
            results = session.query(Company,UserCompany,User)\
            .join(UserCompany,UserCompany.idCompany == Company.id,isouter=True)\
            .join(User,UserCompany.idUser == User.id,isouter=True)\
            .filter(Company.idUser == current_user.id,Company.id == id).all()
            return render_template('company.html',company_info = results,current_user=current_user)
        
        elif request.method == 'POST' and request.form:
            dict_data = request.form.to_dict()
            dict_data['idUser'] = current_user.id
            company = Company(**dict_data)
            session = Session()
            session.add(company)
            session.commit()
            session.close()
            return url_for('/profile')
        
@app.route('/signup_worker/<id_company>',methods=['GET','POST'])
def signup_worker(id_company=None):
    if request.method == 'GET':
        return render_template('htmx/signup.html',data={'return':f'/signup_worker/{id_company}'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password'])
        dict_data['userTypeId'] = 2 #Worker
        dict_data['is_active'] = 0 #Has to be enabled manually
        
        user = User(**dict_data)
        session = Session()
        session.add(user)
        session.commit()

        usercompany = UserCompany(idUser =user.id,idCompany=id_company)         
        session.add(usercompany)
        session.commit()
        session.close()

        return redirect(f'/company/{id_company}')