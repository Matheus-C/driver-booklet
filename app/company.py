from flask import render_template, request, url_for, redirect,jsonify, flash, abort, Response, make_response
from app.models.models import *
from app.models.database import *
from app import app,bcrypt
from flask_login import current_user,login_required
from sqlalchemy.sql import text

@app.route("/companies", methods=["GET"])
@login_required
def companies():
    if current_user:
        if request.method == 'GET':
            session = Session()
            results = session.query(Company).filter(Company.idUser == current_user.id).all()
            session.close()
            return render_template('companies.html',current_user=current_user,companies=results)

@app.route("/company", methods=["GET","POST"])
@login_required
def company():
    if current_user:
        
        if request.method == 'GET':
            return render_template('htmx/company/company_add_form.html',current_user=current_user)
        
        elif request.method == 'POST' and request.form:
            dict_data = request.form.to_dict()
            dict_data['idUser'] = current_user.id
            
            session = Session()
            #checks if exists another company with the same vatcode
            if(session.query(Company).filter(Company.vatcode==dict_data['vatcode']).first() != None):
                flash("Vatcode já registrado.", "error")
                return render_template('base/notifications.html')
            # Add Company
            company = Company(**dict_data)
            session.add(company)
            session.commit()
            
            # Add userCompany
            user_company = UserCompany(idUser = current_user.id,idCompany = company.id, startWork = '1900-01-01')
            session.add(user_company)
            session.commit()
            session.close()
            flash("Registrado com sucesso.", "success")
            response = Response()
            response.headers["hx-redirect"] = "/companies"
            return response
        
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
                    UserCompany.validUntil == None
                    ).all()
            
            vehicles_company = session.query(Vehicle)\
            .join(CompanyVehicle,CompanyVehicle.idVehicle == Vehicle.id,isouter=True)\
            .filter(CompanyVehicle.idCompany == id,
                    CompanyVehicle.validUntil == None).all()
            
            company = session.query(Company)\
            .filter(Company.idUser == current_user.id,
                    Company.id == id).one()
            
            query = f"""
            SELECT 
                max(e."eventTime") as "e.eventTime"
                ,et.name "eventName"
                ,e."idUser"
                ,v.model
                ,v."licensePlate"
                ,e.geolocation
                ,u.name

            FROM event e
            inner join "eventType" et on et.id = e."idType"
            left join "companyVehicle" cv on cv."idVehicle" = e."idVehicle" and cv."validUntil" is null
            left join "userCompany" uc on uc."idCompany" = e."idCompany" and uc."validUntil" is null
            inner join vehicle v on v.id = cv."idVehicle"
            inner join users u on u.id = uc."idUser"
            where 1=1
            and uc."idCompany" = {int(id)}
            group by
                et.name
                ,e."idUser"
                ,v.model
                ,v."licensePlate"
                ,e.geolocation
                ,u.name;            
            """
            query = text(query)
            session = Session()
            geolocation = session.execute(query).all()
            session.close()
            return render_template('htmx/company/company.html',company = company,users_company = users_company, vehicles_company = vehicles_company,geolocation=geolocation,current_user=current_user)
        
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
        return render_template('htmx/user/signup.html',data={'return':f'/signup_worker/{id_company}'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        session = Session()
        if(session.query(User).filter(User.userIdentification==dict_data['userIdentification']).first() != None or\
           session.query(User).filter(User.email==dict_data['email']).first() != None):
            flash("Usuário já registrado.", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#signup_form .containerNotifications"
            return response
        dict_data['password'] = bcrypt.generate_password_hash(password=dict_data['password'])
        dict_data['userTypeId'] = 2 #Worker
        start_work = dict_data['startWorkDate']
        dict_data.pop('startWorkDate')
        # dict_data['is_active'] = 0 #Has to be enabled manually
        
        user = User(**dict_data)
        user._mail_verified = True
        session.add(user)
        session.commit()
        usercompany = UserCompany(idUser =user.id,idCompany=id_company, startWork = start_work)         
        session.add(usercompany)
        session.commit()
        session.close()
        flash("Registrado com sucesso.", "success")
        
        return redirect(f'/worker/list/{id_company}')
    
@app.route('/company/list',methods=['GET'])
@login_required
def company_list():
    if current_user:
        session = Session()
        results = session.query(Company)\
            .join(UserCompany,UserCompany.idCompany == Company.id,isouter=True)\
            .filter(UserCompany.idUser == current_user.id, UserCompany.validUntil == None).all()
        session.close()
        return render_template('htmx/company/company_list.html',company_list = results)
    
@app.route('/geolocation/list/<id>',methods=['GET'])
@login_required
def geolocation_list(id):
    if current_user:
        query = f"""
        SELECT 
            max(e."eventTime") as "eventTime"
            ,et.category "eventCategory"
            ,e."idUser"
            ,v.model
            ,v."licensePlate"
            ,e.geolocation
            ,u.name

        FROM event e
        inner join "eventType" et on et.id = e."idType"
        left join "companyVehicle" cv on cv."idVehicle" = e."idVehicle" and cv."validUntil" is null
        left join "userCompany" uc on uc."idCompany" = e."idCompany" and uc."validUntil" is null
        inner join vehicle v on v.id = cv."idVehicle"
        inner join users u on u.id = uc."idUser"
        where 1=1
        and uc."idCompany" = {int(id)}
        group by 
            et.category
            ,e."idUser"
            ,v.model
            ,v."licensePlate"
            ,e.geolocation
            ,u.name;            
        """
        query = text(query)
        session = Session()
        result = session.execute(query).all()
        session.close()
        if result is not None:
            data=[]
            for entry in result:
                data.append({
                    'eventTime':entry.eventTime,
                    'eventCategory':entry.eventCategory,
                    'userName':entry.name, 
                    'model':entry.model,
                    'licensePlate':entry.licensePlate,
                    'latitude':entry.geolocation.split(',')[0],
                    'longitude':entry.geolocation.split(',')[1]
            })

        else: 
             data=[]
        return jsonify(data)

    
@app.route('/worker/list/<id>',methods=['GET'])
@login_required
def worker_list(id):
    if current_user:
        session = Session()
        results = session.query(User)\
        .join(UserCompany, UserCompany.idUser == User.id,isouter=True)\
        .filter(UserCompany.idCompany == id,
                UserCompany.validUntil == None).all()
        
        session.close()
        return render_template('htmx/company/workers.html', workers = results)

# @app.route('/vehicle/list/<id>',methods=['GET'])
# @login_required
# def vehicle_list(id):
#     if current_user:
#         session = Session()
#         results = session.query(Vehicle)\
#         .join(CompanyVehicle, CompanyVehicle.idVehicle == Vehicle.id,isouter=True)\
#         .filter(CompanyVehicle.idCompany == id,
#                 CompanyVehicle.validUntil == None).all()
        
#         session.close()
#         return render_template('htmx/vehicle/vehicles.html', vehicles = results)