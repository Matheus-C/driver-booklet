from flask import render_template, request, jsonify, redirect
from flask_login import login_required, current_user
from datetime import datetime
from app import app
from app.models.models import *


@app.route('/timer')
@login_required
def timer():
    if current_user:
        return render_template('timer.html', current_user=current_user)
    else:
        return redirect('/')


@app.route("/event_data", methods=["POST"])
@login_required
def event_data():
    session = Session()
    json_data = request.form.to_dict()
    dt_object = datetime.strptime(json_data["eventTimestamp"], '%m/%d/%Y, %H:%M:%S')

    geolocation = Geolocation(coordinates=json_data["geolocation"], address=None)
    session.add(geolocation)
    session.flush()

    event = Event(eventTimestamp=dt_object.strftime("%Y-%m-%d %H:%M:%S"), idType=json_data["idType"],
                  idUser=current_user.id, idVehicle=json_data["idVehicle"], idCompany=json_data["idCompany"],
                  idGeolocation=geolocation.id)
    session.add(event)
    session.commit()
    session.close()
    return jsonify({"status": "success"})


@app.route('/timer/update/<id>')
@login_required
def timer_update(id):
    # needs validation before querying
    query = f"""
    WITH event_query as 
                (SELECT e."eventTime" "dateStart",
                        et.category,
                        case when et.name like '%_end' then null
                        ELSE LEAD("eventTime", 1, null) OVER (ORDER BY "eventTime" ASC)
                        END as "dateEnd",
                        e."idVehicle",
                        e."idCompany",
                        g.coordinates
                FROM event e
                INNER JOIN "eventType" et ON et.id = e."idType"
                join geolocation g on g.id = e."idGeolocation"
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

        return render_template('htmx/timer/timer_updates.html', data=data)
    else:
        return redirect('/')


@app.route('/timer/progress/<id>')
@login_required
def timer_progress(id):
    if current_user:
        session = Session()
        last_event = session.query(VehicleEvent).filter(VehicleEvent.idUser == id).order_by(VehicleEvent.eventTime.desc()).first()
        query = f"""
                    WITH event_query as 
                    (SELECT e."createdAt" "dateStart",
                            et.category,
                            et.name_pt,
                            case when et.name like '%_end' then null
                            ELSE LEAD(e."createdAt", 1, NOW()) OVER (ORDER BY e."createdAt" ASC)
                            END as "dateEnd",
                            e."idVehicle",
                            e."idCompany",
                            g.coordinates
                    FROM event e
                    INNER JOIN "eventType" et ON et.id = e."idType"
                    join geolocation g on g.id = e."idGeolocation"
                    WHERE e."idUser" = {id}
                    and e."idCompany" = {int(last_event.idCompany)}
                    and e."idVehicle" = {int(last_event.idVehicle)}
                    and date(e."createdAt") between CURRENT_DATE and CURRENT_DATE
                    )
                
                select 
                    e.category, e.name_pt "categoryName"
                    ,sec_to_time(SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart")))) AS "timeSpent"
                    ,CASE
                        WHEN e.category = 'availability' THEN SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart"))) / 50400
                        WHEN e.category = 'work' THEN SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart"))) / 36000
                        WHEN e.category = 'rest' THEN SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart"))) / 50400
                        END as percentage_total
                from event_query e
                where "dateEnd" is not null
                group by e.category, "categoryName"
                order by e.category desc
                """

        query = text(query)

        data = session.execute(query).all()
        session.close()

        return render_template('htmx/timer/timer_progress.html', data=data)
    else:
        return redirect('/')
