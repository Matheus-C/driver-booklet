from flask import render_template, request, flash, make_response, jsonify,send_file,redirect
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import login_required,current_user
from datetime import datetime
from sqlalchemy.sql import text


@app.route("/attachment", methods=['GET'])
@login_required
def attachments():
    if current_user:
        if request.method == 'GET':
            session = Session()
            attachments = session.query(Attachment).filter(Attachment.idUser == current_user.id).order_by(Attachment.createdAt.desc()).all()
            return render_template("attachments.html", attachments = attachments, current_user = current_user)

@app.route("/attachment/new", methods=['GET', 'POST'])
@login_required
def new_attachment():
    if current_user:
        if request.method == 'GET':
            return render_template('htmx/attachment/new_attachment.html', current_user=current_user)
        elif request.method == 'POST':
            json_data = request.form.to_dict()
            if not "type" in json_data or not "idVehicle" in json_data or not "idCompany" in json_data or not "subject" in json_data:
                flash("Os campos tipo de incidente, veículo, assunto e empresa são obrigatórios", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#attachment_form .containerNotifications"
                return response
            session = Session()
            attachment = Attachment(idUser = current_user.id, idCompany = json_data["idCompany"], 
                                    idType = json_data["type"], description = json_data["description"],
                                    idVehicle = json_data["idVehicle"], subject = json_data["subject"])
            session.add(attachment)
            session.commit()
            session.close()
            flash("Registrado com sucesso.", "success")
            return redirect("/attachment/list")
        
@app.route("/attachment/list", methods=['GET'])
@login_required
def attachments_list():
    if current_user:
        if request.method == 'GET':
            session = Session()
            attachments = session.query(Attachment).filter(Attachment.idUser == current_user.id).order_by(Attachment.createdAt.desc()).all()
            return render_template("htmx/attachment/attachments_list.html", attachments = attachments, current_user = current_user)