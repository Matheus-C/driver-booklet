from datetime import datetime
from flask import jsonify, render_template, request, url_for, redirect
from app.models.models import *
from app.models.database import *
from app import app,bcrypt
from flask_login import current_user,login_required

        
@app.route('/vehicle/add/<id_company>',methods=['GET','POST'])
def vehicle_add(id_company=None):
    if request.method == 'GET':
        return render_template('htmx/vehicle_add_form.html',data={'return':f'/vehicle/add/{id_company}'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        
        vehicle = Vehicle(**dict_data)
        session = Session()
        session.add(vehicle)
        session.commit()
        dt_object = datetime.now()
        company_vehicle = CompanyVehicle(idCompany = id_company, 
                                         idVehicle = vehicle.id, 
                                         startDate = dt_object.strftime("%Y-%m-%d"))
        session.add(company_vehicle)
        session.commit()
        session.close()

        return redirect(f'/company/{id_company}')
    
@app.route('/vehicle/mileage',methods=['POST'])
def mileage_add():
    session = Session()
    json_data = request.get_json()
    dt_object = datetime.fromtimestamp(int(json_data["eventTimestamp"])/1000)
    vehicleEvent = VehicleEvent(eventTime = dt_object, mileage = json_data["mileage"],
                                 idVehicle = json_data["idVehicle"], idCompany = json_data["idCompany"], 
                                 idAttachment = json_data["idAttachment"], idType = json_data["idType"], idUser = current_user.id)
    session.add(vehicleEvent)
    session.commit()
    session.close()
    return jsonify({"status": "success"})

@app.route('/vehicle/list/',methods=['POST'])
def vehicle_list():
    
    if(current_user):
        id_company = request.form.get("idCompany")
        session = Session()
        results = session.query(Vehicle)\
            .join(CompanyVehicle, CompanyVehicle.idVehicle == Vehicle.id)\
            .filter(CompanyVehicle.idCompany == id_company).all()
        session.close()
        return render_template('htmx/vehicle_list.html',vehicle_list = results)

@app.route('/vehicle/current_mileage',methods=['POST'])
@login_required
def current_mileage():
    if current_user:
        # rework with more joins to be safer
        idVehicle = request.form.get('idVehicle')
        session = Session()
        result = session.query(func.max(VehicleEvent.mileage)).filter(VehicleEvent.idVehicle == idVehicle).scalar()
        session.close()

        if result is None:
            result = 0
        return f"""<input min="{str(result)}" value="{str(result)}" id="mileage" name='mileage' class='input' type="number" step="0.01">"""