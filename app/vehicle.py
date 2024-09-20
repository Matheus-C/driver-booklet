from flask import jsonify, render_template, request, redirect, flash, make_response
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user, login_required
from sqlalchemy.sql import text
from datetime import datetime


@app.route('/vehicle/list/<id_company>', methods=['GET'])
def vehicle_list(id_company=None):
    vehicles_company = session.query(Vehicle) \
        .join(CompanyVehicle, CompanyVehicle.idVehicle == Vehicle.id, isouter=True) \
        .filter(CompanyVehicle.idCompany == id_company,
                CompanyVehicle.validUntil == None).all()
    session.close()
    return render_template("htmx/vehicle/vehicle_list.html", vehicles_company=vehicles_company)


@app.route('/vehicle/add/<id_company>', methods=['GET', 'POST'])
def vehicle_add(id_company=None):
    if request.method == 'GET' and current_user.userTypeId == 1:
        return render_template('htmx/vehicle/vehicle_add_form.html', data={'return': f'/vehicle/add/{id_company}'})

    elif request.method == 'POST' and request.form and current_user.userTypeId == 1:
        dict_data = request.form.to_dict()

        if dict_data.get('model') == "" or dict_data.get('manufacturer') == "" or dict_data.get('color') == "":
            flash("Os campos com * são obrigatórios.", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#vehicle_form .containerNotifications"
            return response

        if len(dict_data.get('licensePlate')) < 8:
            flash("Preencha a placa corretamente.", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#vehicle_form .containerNotifications"
            return response

        session = Session()
        if session.query(Vehicle).filter(Vehicle.licensePlate == dict_data['licensePlate']).first() is not None:
            flash("Placa já registrada.", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#vehicle_form .containerNotifications"
            return response


        vehicle = Vehicle(**dict_data)

        session.add(vehicle)
        session.flush()
        dt_object = datetime.now()
        company_vehicle = CompanyVehicle(idCompany=id_company,
                                         idVehicle=vehicle.id,
                                         startDate=dt_object.strftime("%Y-%m-%d"))
        session.add(company_vehicle)
        session.commit()
        session.close()
        flash("Registrado com sucesso.", "success")
        return redirect(f'/vehicle/list/{id_company}')


@app.route('/vehicle/mileage', methods=['POST'])
def mileage_add():
    session = Session()
    json_data = request.form.to_dict()

    last_event = session.query(VehicleEvent).filter(VehicleEvent.idUser == current_user.id).order_by(VehicleEvent.id.desc()).first()
    if last_event is not None:
        if json_data["idType"] != "8" and last_event.idType == 7:
            return jsonify({"status": "success"})
    dt_object = datetime.strptime(json_data["eventTimestamp"], '%m/%d/%Y, %H:%M:%S')
    vehicleEvent = VehicleEvent(eventTime=dt_object, mileage=json_data["mileage"],
                                idVehicle=json_data["idVehicle"], idCompany=json_data["idCompany"],
                                idType=json_data["idType"], idUser=current_user.id)
    session.add(vehicleEvent)
    session.commit()
    session.close()
    return jsonify({"status": "success"})


@app.route('/vehicle/select/', methods=['POST'])
def vehicle_select():
    if current_user:
        id_company = request.form.get("idCompany")
        if id_company == '' or id_company == 'None':
            return ''
        query = f"""with event_vehicle_ranked as (
                    select e.*,et.name,
                            LAST_VALUE(et.name) OVER (
                            PARTITION BY e."idVehicle"
                            ORDER BY e."eventTime" asc
                            RANGE BETWEEN
                            UNBOUNDED PRECEDING 
                            AND
                            UNBOUNDED FOLLOWING) as last_state

                    from event e inner join "eventType" et on et.id = e."idType" ), groupped_vehicle as ( select 
                    v.id,v.model,v."licensePlate", v.color, v.manufacturer, Coalesce(evr.last_state, 'no_event') 
                    last_state from "companyVehicle" cv left join vehicle v on v.id = cv."idVehicle" left join 
                    event_vehicle_ranked evr on evr."idVehicle" =  cv."idVehicle" where cv."idCompany" = {id_company}
                        group by v.id,v.model,v."licensePlate", evr.last_state, v.color, v.manufacturer
                    )
                    select * 
                    from groupped_vehicle; """

        query = text(query)
        session = Session()
        results = session.execute(query).all()
        session.close()
        return render_template('htmx/vehicle/vehicle_select.html', vehicle_list=results)


@app.route('/vehicle/current_mileage', methods=['POST'])
@login_required
def current_mileage():
    if current_user:
        # rework with more joins to be safer
        idVehicle = request.form.get('idVehicle')
        if len(idVehicle) == 0 or idVehicle is None or idVehicle == 'None':
            return f"""<input min="" value="" id="mileage" name='mileage' class='input' 
        type="number" step="0.01">"""
        else:
            session = Session()
            result = session.query(func.max(VehicleEvent.mileage)).filter(VehicleEvent.idVehicle == idVehicle).scalar()
            session.close()

            if result is None:
                result = 0
            return f"""<input min="{str(result)}" value="{str(result)}" id="mileage" name='mileage' class='input' 
            type="number" step="0.01">"""


@app.route('/vehicle/last_state/<id>', methods=['GET'])
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
        result = session.execute(query).first()
        session.close()
        if result is not None:
            formatted_time_string = result.eventTime.strftime("%Y-%m-%dT%H:%M:%S")
            data = {
                'eventTime': formatted_time_string,
                'idVehicle': result.idVehicle,
                'eventName': result.name
            }

        else:
            data = {}
        return jsonify(data)


@app.route('/vehicle/delete/<id>', methods=['DELETE'])
@login_required
def delete_vehicle(id):
    if request.method == 'DELETE' and current_user.userTypeId == 1:
        session = Session()
        vehicle = session.query(CompanyVehicle).filter(CompanyVehicle.idVehicle == id).first()
        vehicle.validUntil = datetime.now().strftime("%Y-%m-%d")
        session.commit()
        vehicles_company = session.query(Vehicle) \
            .join(CompanyVehicle, CompanyVehicle.idVehicle == Vehicle.id, isouter=True) \
            .filter(CompanyVehicle.idCompany == vehicle.idCompany,
                    CompanyVehicle.validUntil == None).all()
        session.close()
        return render_template("htmx/vehicle/vehicle_list.html", vehicles_company=vehicles_company)


@app.route('/vehicle/rest/<id>', methods=['GET'])
def get_rest_time(id):
    session = Session()
    last_start = (session.query(VehicleEvent).filter(VehicleEvent.idVehicle == int(id), VehicleEvent.idType == 7)
                  .order_by(VehicleEvent.id.desc()).first())
    query = f"""with rest as (select 
                case when et.name like '%_end' or et.name not like 'rest%' then null
                    ELSE extract(EPOCH FROM(LEAD(e."createdAt", 1, null) OVER (ORDER BY e."createdAt" asc) - e."createdAt"))
                    END as "restTime"
                FROM event e
                INNER JOIN "eventType" et ON et.id = e."idType"
                where e."idVehicle" = {int(id)}
                and e."createdAt" between '{last_start.createdAt}' and Now()),
                
                last_event as (
                        select "createdAt"
                        from event
                        where "idVehicle" = {int(id)}
                        order by id desc
                        limit 1)
                            
                select sum(rest."restTime") as "restTime", last_event."createdAt"
                from rest, last_event
                group by last_event."createdAt"
            """
    total_rest_time = session.execute(text(query)).first()
    if total_rest_time.restTime is None:
        rest_time = 0
    else:
        rest_time = total_rest_time.restTime
    session.close()
    data = {
        'eventTime': total_rest_time.createdAt,
        'total_rest_time': rest_time,
        'last_start': last_start.createdAt
    }
    return jsonify(data)
