from math import ceil

from flask import render_template, request, flash, make_response, redirect
from flask_login import login_required, current_user
from datetime import datetime
from app import app
from app.models.models import *


class Page(object):

    def __init__(self, items, page, page_size, total):
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(ceil(total / float(page_size)))
        self.page = page


def paginate(id, page, page_size):
    if page <= 0:
        raise AttributeError('page needs to be >= 1')
    if page_size <= 0:
        raise AttributeError('page_size needs to be >= 1')
    query = f""" SELECT attachment.id, timezone('wet', attachment."createdAt") as "createdAt", "eventType".name_pt
                        FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                        WHERE attachment."idUser" = {int(id)}
                        ORDER BY "createdAt" DESC
                        
                        limit {page_size}
                        offset ({page} - 1) * {page_size}
                        
                    """
    query = text(query)
    session = Session()
    attachments = session.execute(query).all()

    total = session.query(Attachment).filter(Attachment.idUser == int(id)).count()
    session.close()
    return Page(attachments, page, page_size, total)


@app.route("/attachment", methods=['GET'])
@login_required
def attachments():
    if current_user and request.method == 'GET':
        return render_template("attachments.html", current_user=current_user)


@app.route("/attachment/add/<page>", methods=['GET', 'POST'])
@login_required
def new_attachment(page):
    if current_user and request.method == 'GET':
        return render_template('htmx/attachment/new_attachment.html', current_user=current_user, page=page)

    elif current_user and request.method == 'POST':
        json_data = request.form.to_dict()
        if "type" not in json_data or "idVehicle" not in json_data or "idCompany" not in json_data or "start_date" \
                not in json_data or "end_date" not in json_data:
            flash("Os campos marcados com * são obrigatórios", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#modalSection .containerNotifications"
            return response

        elif json_data["idVehicle"] == "None" or json_data["idCompany"] == "None":
            flash("Os campos marcados com * são obrigatórios", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#modalSection .containerNotifications"
            return response

        elif datetime.strptime(json_data["start_date"], "%Y-%m-%d").date() > datetime.strptime(
                json_data["end_date"], "%Y-%m-%d").date():
            flash("O campo data início não pode ser uma data após a data fim.", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#modalSection .containerNotifications"
            return response

        session = Session()
        attachment = Attachment(idUser=current_user.id, idCompany=json_data["idCompany"],
                                idType=json_data["type"], description=json_data["description"],
                                idVehicle=json_data["idVehicle"], start_date=json_data["start_date"],
                                end_date=json_data["end_date"])
        session.add(attachment)
        session.commit()
        session.close()
        flash("Incidente registrado com sucesso.", "success")
        if page == "timer":
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#timer .containerNotifications"
            return response

        return redirect("/attachment/list")


@app.route("/attachment/list/<n>", methods=['GET'])
@login_required
def attachments_list(n):
    if current_user and request.method == 'GET':
        page = paginate(current_user.id, int(n), 10)
        return render_template("htmx/attachment/attachments_list.html",
                               attachments=page.items, page=page, current_user=current_user)


@app.route("/attachment/detail/<id>", methods=['GET'])
@login_required
def attachment_detail(id):
    if current_user and request.method == 'GET':
        query = f""" SELECT attachment.id, timezone('wet', attachment."createdAt") as "createdAt",
                     "eventType".name_pt, attachment.start_date, attachment.end_date, attachment.description
                    FROM attachment join "eventType" ON "eventType".id = attachment."idType"
                    WHERE attachment.id = {int(id)} 
                    ORDER BY attachment."createdAt" DESC
                """
        query = text(query)
        session = Session()
        attachment = session.execute(query).first()
        session.close()
        return render_template("htmx/attachment/attachment_details.html", attachment=attachment)


@app.route("/attachment/edit/<id>", methods=['GET', 'POST'])
@login_required
def attachment_edit(id):
    if current_user and request.method == 'GET':
        session = Session()
        attachment = session.query(Attachment).filter(Attachment.id == id).first()
        session.close()
        return render_template('htmx/attachment/edit_attachment.html', attachment=attachment,
                               data={'return': f'/attachment/edit/{id}'})
    elif request.method == 'POST':
        json_data = request.form.to_dict()
        session = Session()
        session.query(Attachment).filter(Attachment.id == id).update(
            {'idCompany': json_data["idCompany"],
             'idType': json_data["type"], 'description': json_data["description"],
             'idVehicle': json_data["idVehicle"], 'start_date': json_data["start_date"],
             'end_date': json_data["end_date"]})
        session.commit()
        session.close()
        return redirect("/attachment/list")
