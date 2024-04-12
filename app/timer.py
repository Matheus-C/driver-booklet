from flask import render_template, request, jsonify,send_file
from app.models.models import *
from app.models.database import *
from app import app
import datetime

@app.route("/event_data", methods=["POST"])
def event_data():
    session = Session()
    json_data = request.get_json()
    dt_object = datetime.datetime.fromtimestamp(int(json_data["eventTimestamp"])/1000)
    print(dt_object)
    event = Event(eventTimestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S"), idType=json_data["idType"], 
                  idUser = json_data["idUser"], vehicleId = json_data["vehicleId"])
    session.add(event)
    session.commit()
    return jsonify({"status": "success"})