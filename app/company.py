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
            return redirect(url_for('profile'))
        
@app.route("/company/<id>", methods=["GET","POST"])
@login_required
def company_info(id):
    if current_user:
        session = Session()
        # try:
        if request.method == 'GET':
            
            users_company = session.query(User)\
            .join(UserCompany,UserCompany.idUser == User.id,isouter=True)\
            .filter(UserCompany.idCompany == id,
                    UserCompany.validUntil == None).all()
            vehicles_company = session.query(Vehicle)\
            .join(CompanyVehicle,Vehicle.id == CompanyVehicle.idVehicle,isouter=True)\
            .filter(CompanyVehicle.idCompany == id,
                    CompanyVehicle.validUntil == None).all()
            company = session.query(Company)\
            .filter(Company.idUser == current_user.id,
                    Company.id == id).one()
            return render_template('company.html',company = company,users_company = users_company, vehicles_company = vehicles_company,current_user=current_user)
        
        elif request.method == 'POST' and request.form:
            dict_data = request.form.to_dict()
            dict_data['idUser'] = current_user.id
            company = Company(**dict_data)
            session.add(company)
            session.commit()
            session.close()
            return redirect('/profile')
        # except:
            # return redirect('/profile')
        
@app.route('/signup_worker/<id_company>',methods=['GET','POST'])
def signup_worker(id_company=None):
    if request.method == 'GET':
        return render_template('htmx/signup.html',data={'return':f'/signup_worker/{id_company}'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password'])
        dict_data['userTypeId'] = 2 #Worker
        start_work = dict_data['startWorkDate']
        dict_data.pop('startWorkDate')
        # dict_data['is_active'] = 0 #Has to be enabled manually
        
        user = User(**dict_data)
        session = Session()
        session.add(user)
        session.commit()

        usercompany = UserCompany(idUser =user.id,idCompany=id_company, startWork = start_work)         
        session.add(usercompany)
        session.commit()
        session.close()

        return redirect(f'/company/{id_company}')
    
@app.route('/company/list',methods=['GET'])
@login_required
def company_list():
    if(current_user):
        session = Session()
        results = session.query(Company)\
            .join(UserCompany,UserCompany.idCompany == Company.id,isouter=True)\
            .filter(UserCompany.idUser == current_user.id, UserCompany.validUntil == None).all()
        session.close()
        return render_template('htmx/company_list.html',company_list = results)