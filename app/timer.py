from flask import render_template, request, jsonify,send_file,redirect
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import login_required,current_user
from datetime import datetime
from sqlalchemy.sql import text

@app.route('/timer')
@login_required
def timer():
    if current_user:
        return render_template('timer_2.html',current_user=current_user)
    else:
        return redirect('/')

@app.route("/event_data", methods=["POST"])
@login_required
def event_data():
    session = Session()
    json_data = request.form.to_dict()
    dt_object =  datetime.strptime(json_data["eventTimestamp"], '%m/%d/%Y, %H:%M:%S')
    event = Event(eventTimestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S"), idType=json_data["idType"], 
                  idUser = current_user.id, idVehicle = json_data["idVehicle"], idCompany = json_data["idCompany"], 
                  geolocation = json_data["geolocation"])
    session.add(event)
    session.commit()
    session.close()
    return jsonify({"status": "success"})

@app.route('/timer/update/<id>')
@login_required
def timer_update(id):
    ## needs validation before querying
    query = f"""
    WITH event_query as 
                (SELECT e.eventTime dateStart,
                        et.category,
                        case when et.name like '%_end' then 0
                        ELSE LEAD(eventTime, 1, 0) OVER (PARTITION BY et.category ORDER BY eventTime ASC) 
                        END as dateEnd,
                        e.idVehicle,
                        e.idCompany,
                        e.geolocation,
                        e.idAttachment
                FROM `event` e
                INNER JOIN `eventType` et ON et.id = e.idType
                WHERE idUser = {id}
                )
            
            select 
                e.dateStart
                ,e.dateEnd      
                ,e.category categoryName
                ,SEC_TO_TIME(TIMESTAMPDIFF(SECOND,dateStart,dateEnd)) AS timeSpent
            from event_query e
            where dateEnd <> 0
            order by dateStart desc
    """
    if current_user:
        query = text(query)
        session = Session()
        data = session.execute(query).fetchmany(5)
        session.close()

        return render_template('htmx/timer_updates.html',data=data)
    else:
        return redirect('/')
    
@app.route('/timer/progress/<id>')
@login_required
def timer_progress(id):
    session = Session()
    query = f"""
                WITH event_query as 
                (SELECT e.eventTime dateStart,
                        et.category,
                        case when et.name like '%_end' then 0
                        ELSE LEAD(eventTime, 1, 0) OVER (PARTITION BY et.category ORDER BY eventTime ASC) 
                        END as dateEnd,
                        e.idVehicle,
                        e.idCompany,
                        e.geolocation,
                        e.idAttachment
                FROM `event` e
                INNER JOIN `eventType` et ON et.id = e.idType
                WHERE idUser = {id}
                and e.eventTime >= DATE_ADD(CURDATE(), INTERVAL 0 HOUR)
                )
            
            select 
                e.category categoryName
                ,SEC_TO_TIME(SUM(TIMESTAMPDIFF(SECOND,dateStart,dateEnd))) AS timeSpent
                ,CASE
                	WHEN e.category = 'availability' THEN SUM(TIMESTAMPDIFF(SECOND,dateStart,dateEnd)) / 50400
                    WHEN e.category = 'work' THEN SUM(TIMESTAMPDIFF(SECOND,dateStart,dateEnd)) / 36000
                    WHEN e.category = 'rest' THEN SUM(TIMESTAMPDIFF(SECOND,dateStart,dateEnd)) / 50400
                    END as percentage_total
            from event_query e
            where dateEnd <> 0
            group by e.category
            order by e.category desc
            """
    if current_user:
        query = text(query)
        session = Session()
        data = session.execute(query).all()
        session.close()

        return render_template('htmx/timer_progress.html',data=data)
    else:
        return redirect('/')