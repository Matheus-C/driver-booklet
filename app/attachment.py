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
            query = f""" SELECT attachment.id, attachment."idUser", attachment."createdAt", "eventType".name_pt 
                        FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                        WHERE attachment."idUser" = {int(current_user.id)} 
                        ORDER BY attachment."createdAt" DESC
                    """
            query = text(query)
            session = Session()
            attachments = session.execute(query).all()
            return render_template("attachments.html", attachments = attachments, current_user = current_user)

@app.route("/attachment/add/<page>", methods=['GET', 'POST'])
@login_required
def new_attachment(page):
    if current_user:
        if request.method == 'GET':
            return render_template('htmx/attachment/new_attachment.html', current_user=current_user, page = page)
        elif request.method == 'POST':
            json_data = request.form.to_dict()
            if not "type" in json_data or not "idVehicle" in json_data or not "idCompany" in json_data or not "start_date" in json_data or not "end_date" in json_data:
                flash("Os campos tipo de incidente, data de inicio e fim, veículo e empresa são obrigatórios", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#modalSection .containerNotifications"
                return response
            elif datetime.strptime(json_data["start_date"], "%Y-%m-%d").date() > datetime.strptime(json_data["end_date"], "%Y-%m-%d").date():
                flash("O campo data início não pode ser uma data após a data fim.", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#modalSection .containerNotifications"
                return response
            session = Session()
            attachment = Attachment(idUser = current_user.id, idCompany = json_data["idCompany"], 
                                    idType = json_data["type"], description = json_data["description"],
                                    idVehicle = json_data["idVehicle"], start_date = json_data["start_date"],
                                    end_date = json_data["end_date"])
            session.add(attachment)
            session.commit()
            session.close()
            flash("Incidente registrado com sucesso.", "success")
            if page == "timer":
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#timer .containerNotifications"
                return response
            return redirect("/attachment/list")
        
@app.route("/attachment/list", methods=['GET'])
@login_required
def attachments_list():
    if current_user:
        if request.method == 'GET':
            query = f""" SELECT attachment.id, attachment."createdAt", "eventType".name_pt 
                        FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                        WHERE attachment."idUser" = {int(current_user.id)} 
                        ORDER BY attachment."createdAt" DESC
                    """
            query = text(query)
            session = Session()
            attachments = session.execute(query).all()
            return render_template("htmx/attachment/attachments_list.html", attachments = attachments, current_user = current_user)

@app.route("/attachment/detail/<id>", methods=['GET'])
@login_required
def attachment_detail(id):
    if current_user:
        if request.method == 'GET':
            query = f""" SELECT attachment.id, attachment."createdAt",
                         "eventType".name_pt, attachment.start_date, attachment.end_date, attachment.description
                        FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                        WHERE attachment.id = {int(id)} 
                        ORDER BY attachment."createdAt" DESC
                    """
            query = text(query)
            session = Session()
            attachment = session.execute(query).first()
            session.close()
            return render_template("htmx/attachment/attachment_details.html", attachment = attachment)

@app.route("/attachment/edit/<id>", methods=['GET', 'POST'])
@login_required
def attachment_edit(id):
    if current_user:
        if request.method == 'GET':
            session = Session()
            attachment = session.query(Attachment).filter(Attachment.id == id).first()
            session.close()
            return render_template('htmx/attachment/edit_attachment.html', attachment = attachment, data={'return':f'/attachment/edit/{id}'})
        elif request.method == 'POST':
            json_data = request.form.to_dict()
            session = Session()
            attachment = session.query(Attachment).filter(Attachment.id == id).update({'idCompany': json_data["idCompany"], 
                                    'idType': json_data["type"], 'description': json_data["description"],
                                    'idVehicle': json_data["idVehicle"], 'start_date': json_data["start_date"],
                                    'end_date': json_data["end_date"]})
            session.commit()
            session.close()
            return redirect("/attachment/list")