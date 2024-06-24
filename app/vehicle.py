from datetime import datetime
from flask import jsonify, render_template, request, redirect,flash
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required
from sqlalchemy.sql import text
        
@app.route('/vehicle/add/<id_company>',methods=['GET','POST'])
def vehicle_add(id_company=None):
    if request.method == 'GET':
        return render_template('htmx/vehicle/vehicle_add_form.html',data={'return':f'/vehicle/add/{id_company}'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        session = Session()
        if(session.query(Vehicle).filter(Vehicle.licensePlate==dict_data['licensePlate']).first() != None):
            flash("Placa já registrada.", "error")
            return render_template('htmx/vehicle/vehicle_add_form.html', data={'return':f'/vehicle/add/{id_company}'})

        
        vehicle = Vehicle(**dict_data)
        
        session.add(vehicle)
        session.commit()
        dt_object = datetime.now()
        company_vehicle = CompanyVehicle(idCompany = id_company, 
                                         idVehicle = vehicle.id, 
                                         startDate = dt_object.strftime("%Y-%m-%d"))
        session.add(company_vehicle)
        session.commit()
        session.close()
        flash("Registrado com sucesso.", "success")
        return redirect(f'/vehicle/list/{id_company}')
        #return redirect(f'/company/{id_company}')
    
@app.route('/vehicle/mileage',methods=['POST'])
def mileage_add():
    session = Session()
    json_data = request.form.to_dict()
    dt_object =  datetime.strptime(json_data["eventTimestamp"], '%m/%d/%Y, %H:%M:%S')
    vehicleEvent = VehicleEvent(eventTime = dt_object, mileage = json_data["mileage"],
                                 idVehicle = json_data["idVehicle"], idCompany = json_data["idCompany"], 
                                  idType = json_data["idType"], idUser = current_user.id)
    session.add(vehicleEvent)
    session.commit()
    session.close()
    return jsonify({"status": "success"})

@app.route('/vehicle/select/',methods=['POST'])
def vehicle_select():
    
    if(current_user):
        id_company = int(request.form.get("idCompany"))
        query = f"""with event_vehicle_ranked as (
                    select e.*,et.name,
                            LAST_VALUE(et.name) OVER (
                            PARTITION BY e."idVehicle"
                            ORDER BY e."eventTime" asc
                            RANGE BETWEEN
                            UNBOUNDED PRECEDING 
                            AND
                            UNBOUNDED FOLLOWING) as last_state

                    from event e 
                    inner join "eventType" et on et.id = e."idType"
                    ),
                    groupped_vehicle as (
                        select v.id,v.model,v."licensePlate", v.color, v.manufacturer, Coalesce(evr.last_state, 'no_event') last_state
                        from "companyVehicle" cv
                            left join vehicle v on v.id = cv."idVehicle"
                            left join event_vehicle_ranked evr on evr."idVehicle" =  cv."idVehicle"
                        where cv."idCompany" = {id_company}
                        group by v.id,v.model,v."licensePlate", evr.last_state, v.color, v.manufacturer
                    )
                    select * 
                    from groupped_vehicle; """

        query = text(query)
        session = Session()
        results = session.execute(query).all()
        session.close()
        return render_template('htmx/vehicle/vehicle_list.html',vehicle_list = results)

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
    

@app.route('/vehicle/last_state/<id>',methods=['GET'])
@login_required
def last_state_vehicle(id):
    if current_user:
        session = Session()
        query = f""" with max_id_vehicle as (
                select max(id) as id 
                from event 
                where "idVehicle" = {int(id)}
            )
            SELECT e."eventTime",e."idVehicle",et.name 
            FROM event e
            INNER join "eventType" et on et.id = e."idType"
            inner join max_id_vehicle m on m.id = e.id;"""
        
        query = text(query)
        session = Session()
        result = session.execute(query).fetchone()
        session.close()

        if result is not None:
            formatted_time_string = result.eventTime.strftime("%Y-%m-%dT%H:%M:%S")
            data ={
                'eventTime': formatted_time_string,
                'idVehicle': result.idVehicle,
                'eventName': result.name }

        else: 
             data={}
        return jsonify(data)