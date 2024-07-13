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
            query = f""" SELECT attachment.id, attachment."createdAt", "eventType".name 
                        FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                        WHERE attachment."idUser" = {int(current_user.id)} 
                        ORDER BY attachment."createdAt" DESC 
                    """
            query = text(query)
            session = Session()
            attachments = session.execute(query).all()
            return render_template("attachments.html", attachments = attachments, current_user = current_user)

@app.route("/attachment/new", methods=['GET', 'POST'])
@login_required
def new_attachment():
    if current_user:
        if request.method == 'GET':
            return render_template('htmx/attachment/new_attachment.html', current_user=current_user)
        elif request.method == 'POST':
            json_data = request.form.to_dict()
            if not json_data["type"]:
                flash("O campo tipo de incidente é obrigatório", "error")
                response = make_response(render_template('htmx/attachment/new_attachment.html', current_user=current_user))
                response.headers["hx-Retarget"] = "#modal .containerNotifications"
                return response
            session = Session()
            attachment = Attachment(idUser = current_user.id, idCompany = json_data["idCompany"], 
                                    idType = json_data["type"], description = json_data["description"],
                                    idVehicle = json_data["idVehicle"])
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
            query = f""" SELECT attachment.id, attachment."createdAt", "eventType".name 
                        FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                        WHERE attachment."idUser" = {int(current_user.id)} 
                        ORDER BY attachment."createdAt" DESC 
                    """
            query = text(query)
            session = Session()
            attachments = session.execute(query).all()
            return render_template("htmx/attachment/attachments_list.html", attachments = attachments, current_user = current_user)