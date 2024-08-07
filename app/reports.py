from flask import render_template, request, make_response, flash, Response
from flask_login import current_user, login_required
from .models.models import *
from sqlalchemy.sql import text
from app import app
from app.models.database import *
from .email import send_email


def render_pdf(html):
    from xhtml2pdf import pisa
    from io import BytesIO

    pdf = BytesIO()

    pisa.CreatePDF(html, pdf)

    return pdf.getvalue()


def get_report(id_user, dict_data):
    #event query
    query = f"""
                    WITH event_query as 
                    (SELECT e."eventTime" "dateStart",
                            et.category, et.name_pt,
                            case when et.name like '%_end' then null
                            ELSE LEAD("eventTime", 1, null) OVER (ORDER BY "eventTime" ASC)
                            END as "dateEnd",
                            e."idVehicle",
                            e."idCompany",
                            p.address as "locStart",
                            case when et.name like '%_end' then null
                            ELSE LEAD(p.address, 1, null) OVER (ORDER BY "eventTime" ASC)
                            END as "locEnd"
                    FROM event e
                    INNER JOIN "eventType" et ON et.id = e."idType"
                    INNER JOIN positions p ON p.id = e.geolocation
                    WHERE "idUser" = {id_user}
                    and e."idCompany" = {dict_data['idCompany']}
                    and e."eventTime" between (date('{dict_data['dateStart']}') - 1) 
                    and (date('{dict_data['dateEnd']}') + 1)
                    )

                select 
                    c.name "companyName"
                    ,e."dateStart"
                    ,e.name_pt "categoryName"
                    ,"dateEnd"      
                    ,sec_to_time(SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart")))) AS "timeSpent"
                    ,v.model
                    ,v."licensePlate"
                    ,e."locStart"
                    ,e."locEnd"
                from event_query e
                    left join vehicle v on v.id = e."idVehicle"
                    left join company c on c.id = e."idCompany"
                where "dateEnd" is not null
                group by c.name
                    ,e."dateStart"
                    ,e.category
                    ,"dateEnd"
                    ,v.model
                    ,v."licensePlate"
                    ,e."locStart"
                    ,e."locEnd"
                    ,e.name_pt
                order by "dateStart" asc
                    """

    query = text(query)
    session = Session()
    event_data = session.execute(query).all()

    #attachment query
    query = f"""
        select et.name_pt "categoryName", v."licensePlate",
         a.description, a.start_date, a.end_date
        from attachment a 
            inner join "eventType" et on et.id = a."idType"
            inner join vehicle v on v.id = a."idVehicle"
        where a."idUser" = {id_user} and 
            a."idCompany" = {dict_data['idCompany']} and
            a.start_date between date('{dict_data['dateStart']}')-1 and date('{dict_data['dateEnd']}')+1 and
            a.end_date between date('{dict_data['dateStart']}')-1 and date('{dict_data['dateEnd']}')+1
    """
    query = text(query)
    attachment_data = session.execute(query).all()

    #
    query = f"""
                    WITH event_query as 
                    (SELECT e."eventTime" "dateStart",
                            et.category,
                            et.name_pt,
                            case when et.name like '%_end' then null
                            ELSE LEAD(e."eventTime", 1, null) OVER (ORDER BY e."eventTime" ASC)
                            END as "dateEnd",
                            e."idVehicle",
                            e."idCompany",
                            p.address
                    FROM event e
                    INNER JOIN "eventType" et ON et.id = e."idType"
                    join positions p on p.id = e.geolocation
                    WHERE e."idUser" = {id_user}
                    and date(e."eventTime") between date('{dict_data['dateStart']}')-1 
                    and date('{dict_data['dateEnd']}')+1
                    )

                select 
                    e.category "categoryName"
                    ,e.name_pt
                    ,sec_to_time(SUM(EXTRACT(EPOCH FROM ("dateEnd" -"dateStart")))) AS "timeSpent"
                from event_query e
                where "dateEnd" is not null
                group by e.category, e.name_pt
                order by e.category desc
                """
    query = text(query)
    time_data = session.execute(query).all()
    user = session.query(User).filter(User.id == id_user).first()
    company = session.query(Company).filter(Company.id == dict_data["idCompany"]).first()
    session.close()
    return {"event_data": event_data, "attachment_data": attachment_data,
            "user": user, "company": company, "time_data": time_data}


@app.route("/reports", methods=["GET", "POST"])
@login_required
def reports():
    if current_user:
        if request.method == 'GET':
            return render_template('reports.html', current_user=current_user)

        if request.method == 'POST':
            # get companies, that you worked for and cars ?
            if request.form:
                # needs validation before querying
                dict_data = request.form.to_dict()
                if dict_data["idCompany"] == "None" or dict_data["dateStart"] == "" or dict_data["dateEnd"] == "":
                    flash("Os campos com * são obrigatórios.", "error")
                    response = make_response(render_template('base/notifications.html'))
                    response.headers["hx-Retarget"] = "#form-box .containerNotifications"
                    return response
                if current_user.userTypeId == 1:
                    id_user = dict_data["idUser"]
                    if id_user == "None":
                        flash("Os campos com * são obrigatórios.", "error")
                        response = make_response(render_template('base/notifications.html'))
                        response.headers["hx-Retarget"] = "#form-box .containerNotifications"
                        return response
                else:
                    id_user = current_user.id
                data = get_report(id_user, dict_data)
                return render_template('htmx/report/report.html', event_data=data["event_data"],
                                       attachment_data=data["attachment_data"],
                                       user=data["user"], company=data["company"], time_data=data["time_data"],
                                       date_start=dict_data["dateStart"], date_end=dict_data["dateEnd"])
            else:
                flash("Ocorreu um erro, tente novamente", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#form-box .containerNotifications"
                return response


@app.route("/reports/pdf", methods=["POST"])
def pdf_report():
    if request.method == 'POST':
        # get companies, that you worked for and cars ?
        if request.form:
            # needs validation before querying
            dict_data = request.form.to_dict()
            if current_user.userTypeId == 1:
                if "idUser" in dict_data:
                    id_user = dict_data["idUser"]
                else:
                    id_user = "None"
            else:
                id_user = current_user.id
            if dict_data["idUser"] == "None":
                flash("Os campos com * são obrigatórios.", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#form-box .containerNotifications"
                return response
            data = get_report(id_user, dict_data)
            html = render_template("htmx/report/report_pdf_template.html", event_data=data["event_data"],
                                   attachment_data=data["attachment_data"],
                                   user=data["user"], company=data["company"], time_data=data["time_data"],
                                   date_start=dict_data["dateStart"], date_end=dict_data["dateEnd"])
            pdf = render_pdf(html)
            headers = {
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment;filename=report.pdf"
            }
            response = Response(pdf, headers=headers)
            return response
        else:
            flash("Ocorreu um erro, tente novamente", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#form-box .containerNotifications"
            return response


@app.route("/reports/mail", methods=["POST"])
def email_report():
    if request.method == 'POST':
        # get companies, that you worked for and cars ?
        if request.form:
            # needs validation before querying
            dict_data = request.form.to_dict()
            if current_user.userTypeId == 1:
                if "idUser" in dict_data:
                    id_user = dict_data["idUser"]
                else:
                    id_user = "None"
            else:
                id_user = current_user.id
            if id_user == "None" or "email" in dict_data:
                flash("Os campos com * são obrigatórios.", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#form-box .containerNotifications"
                return response
            data = get_report(id_user, dict_data)
            html = render_template("htmx/report/report_pdf_template.html", event_data=data["event_data"],
                                   attachment_data=data["attachment_data"],
                                   user=data["user"], company=data["company"], time_data=data["time_data"],
                                   date_start=dict_data["dateStart"], date_end=dict_data["dateEnd"])
            pdf = render_pdf(html)
            html = render_template('email/email_template.html', url="",
                                   msg="Segue em anexo o relatório requisitado")
            send_email(dict_data["email"],
                       "Relatório DriverBooklet",
                       html, pdf, "application/pdf", "Relatório.pdf")
            flash("O email foi enviado para o endereço cadastrado.", "success")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#form-box .containerNotifications"
            return response
        else:
            flash("Ocorreu um erro, tente novamente", "error")
            response = make_response(render_template('base/notifications.html'))
            response.headers["hx-Retarget"] = "#form-box .containerNotifications"
            return response
