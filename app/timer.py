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
        return render_template('timer.html',current_user=current_user)
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
                (SELECT e."eventTime" "dateStart",
                        et.category,
                        case when et.name like '%_end' then null
                        ELSE LEAD("eventTime", 1, null) OVER (ORDER BY "eventTime" ASC)
                        END as "dateEnd",
                        e."idVehicle",
                        e."idCompany",
                        e.geolocation
                FROM event e
                INNER JOIN "eventType" et ON et.id = e."idType"
                WHERE idUser = {id}
                )
            
            select 
                e."dateStart"
                ,e."dateEnd"      
                ,e.category "categoryName"
                ,sec_to_time(SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart")))) AS "timeSpent"
            from event_query e
            where "dateEnd" is not null
            group by e."dateStart"
                ,e."dateEnd"      
                ,e.category "categoryName"
            order by "dateStart" desc
    """
    if current_user:
        query = text(query)
        session = Session()
        data = session.execute(query).fetchmany(5)
        session.close()

        return render_template('htmx/timer/timer_updates.html',data=data)
    else:
        return redirect('/')
    
@app.route('/timer/progress/<id>')
@login_required
def timer_progress(id):
    session = Session()
    query = f"""
                WITH event_query as 
                (SELECT e."eventTime" "dateStart",
                        et.category,
                        case when et.name like '%_end' then null
                        ELSE LEAD(e."eventTime", 1, null) OVER (ORDER BY e."eventTime" ASC)
                        END as "dateEnd",
                        e."idVehicle",
                        e."idCompany",
                        e.geolocation
                FROM event e
                INNER JOIN "eventType" et ON et.id = e."idType"
                WHERE e."idUser" = 6
                )
            
            select 
                e.category "categoryName"
                ,sec_to_time(SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart")))) AS "timeSpent"
                ,CASE
                	WHEN e.category = 'availability' THEN SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart"))) / 50400
                    WHEN e.category = 'work' THEN SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart"))) / 36000
                    WHEN e.category = 'rest' THEN SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart"))) / 50400
                    END as percentage_total
            from event_query e
            where "dateEnd" is not null
            group by e.category
            order by e.category desc
            """
    if current_user:
        query = text(query)
        session = Session()
        data = session.execute(query).all()
        session.close()

        return render_template('htmx/timer/timer_progress.html',data=data)
    else:
        return redirect('/')
    

@app.route('/timer/mileage', methods=["GET"])
def mileage_form():
    if(request.method == "GET"):
        return render_template("htmx/timer/mileage_form.html")