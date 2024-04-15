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
        return render_template('htmx/timer.html',current_user=current_user)
    else:
        return redirect('/')

@app.route("/event_data", methods=["POST"])
@login_required
def event_data():
    session = Session()
    json_data = request.get_json()
    dt_object = datetime.fromtimestamp(int(json_data["eventTimestamp"])/1000)
    event = Event(eventTimestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S"), idType=json_data["idType"], 
                  idUser = current_user.id, vehicleId = json_data["vehicleId"])
    session.add(event)
    session.commit()
    return jsonify({"status": "success"})

@app.route('/timer/update/<id>')
@login_required
def timer_update(id):
    ## needs validation before querying
    query = f"""
    WITH cleaned_event_names AS
  (SELECT et.id,
          CASE
              WHEN et.name like '%_end' THEN replace(et.name, '_end', '')
              WHEN et.name like '%_start' THEN replace(et.name, '_start', '')
          END AS name,
   		  et.name as old_name,
          et.description
   FROM eventType et),
     lag_query AS
  (SELECT e.eventTime date_start,
          et.name CategoryName,
    	  case when et.old_name like '%_END' then 0
          ELSE LEAD(eventTime, 1, 0) OVER (PARTITION BY et.name ORDER BY eventTime ASC) 
   		 END as date_end
   FROM `event` e
   INNER JOIN cleaned_event_names et ON et.id = e.idType
   WHERE idUser = {id}
   )
   
   select *,TIMESTAMPDIFF(SECOND,date_start,date_end)/3600 AS difference from lag_query
   where date_end <> 0
    order by date_start desc
    """
    if current_user:
        query = text(query)
        session = Session()
        data = session.execute(query).fetchmany(10)

        return render_template('htmx/timer_updates.html',data=data)
    else:
        return redirect('/')