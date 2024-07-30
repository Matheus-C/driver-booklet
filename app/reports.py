from flask import render_template, request, make_response, flash, Response
from flask_login import current_user, login_required
from sqlalchemy.sql import text
from app import app
from app.models.database import *
from pdfkit import from_string


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
                query = f"""
                WITH event_query as 
                (SELECT e."eventTime" "dateStart",
                        et.category,
                        case when et.name like '%_end' then null
                        ELSE LEAD("eventTime", 1, null) OVER (ORDER BY "eventTime" ASC)
                        END as "dateEnd",
                        e."idVehicle",
                        e."idCompany",
                        e.geolocation as "locStart",
                        case when et.name like '%_end' then null
                        ELSE LEAD(e.geolocation, 1, null) OVER (ORDER BY "eventTime" ASC)
                        END as "locEnd"
                FROM event e
                INNER JOIN "eventType" et ON et.id = e."idType"
                WHERE "idUser" = {id_user}
                and e."idCompany" = {dict_data['idCompany']}
                and e."eventTime" between (date('{dict_data['dateStart']}') - 1) 
                and (date('{dict_data['dateEnd']}') + 1)
                )
            
            select 
                c.name "companyName"
                ,e."dateStart"
                ,e.category "categoryName"
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
            order by "dateStart" asc
                """

            query = text(query)
            session = Session()
            data = session.execute(query).all()
            session.close()

            return render_template('htmx/report/report.html', data=data)


@app.route("/reports/pdf", methods=["POST"])
def pdf_report():
    if request.method == 'POST':
        # get companies, that you worked for and cars ?
        if request.form:
            # needs validation before querying
            dict_data = request.form.to_dict()
            if "idUser" in dict_data:
                id_user = dict_data["idUser"]
            else:
                id_user = current_user.id
            if dict_data["idUser"] == "None":
                flash("Selecione um colaborador.", "error")
                response = make_response(render_template('base/notifications.html'))
                response.headers["hx-Retarget"] = "#form-box .containerNotifications"
                return response
            query = f"""
            WITH event_query as 
            (SELECT e."eventTime" "dateStart",
                    et.category,
                    case when et.name like '%_end' then null
                    ELSE LEAD("eventTime", 1, null) OVER (ORDER BY "eventTime" ASC)
                    END as "dateEnd",
                    e."idVehicle",
                    e."idCompany",
                    e.geolocation as "locStart",
                    case when et.name like '%_end' then null
                    ELSE LEAD(e.geolocation, 1, null) OVER (ORDER BY "eventTime" ASC)
                    END as "locEnd"
            FROM event e
            INNER JOIN "eventType" et ON et.id = e."idType"
            WHERE "idUser" = {id_user}
            and e."idCompany" = {dict_data['idCompany']}
            and e."eventTime" between (date('{dict_data['dateStart']}') - 1) 
            and (date('{dict_data['dateEnd']}') + 1)
            )

        select 
            c.name "companyName"
            ,e."dateStart"
            ,e.category "categoryName"
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
        order by "dateStart" asc
            """

        query = text(query)
        session = Session()
        data = session.execute(query).all()
        session.close()
        html = render_template("htmx/report/report_template.html", data=data)
        pdf = from_string(html, False)
        headers = {
            "Content-Type": "application/pdf",
            "Content-Disposition": "attachment;filename=report.pdf"
        }
        response = Response(pdf, headers=headers)
        return response
