from flask import render_template, request, url_for, redirect
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required
from sqlalchemy.sql import text


@app.route("/reports", methods=["GET","POST"])
@login_required
def reports():
    if current_user:
        if request.method == 'GET':
            return render_template('reports.html',current_user=current_user)
        
        if request.method == 'POST':
            # get companies, that you worked for and cars ?
            if request.form:
                ## needs validation before querying
                dict_data = request.form.to_dict()

                query = f"""
                WITH event_query as 
                (SELECT e.eventTime dateStart,
                        et.category,
                        case when et.name like '%_end' then 0
                        ELSE LEAD(eventTime, 1, 0) OVER (ORDER BY eventTime ASC)
                        END as dateEnd,
                        e."idVehicle",
                        e."idCompany",
                        e.geolocation,
                        e.idAttachment
                FROM event e
                INNER JOIN "eventType" et ON et.id = e."idType"
                WHERE idUser = {current_user.id}
                and e."idCompany" = {dict_data['idCompany']}
                and e.eventTime between (date('{dict_data['dateStart']}') - 1) and (date('{dict_data['dateEnd']}') + 1)
                )
            
            select 
                c.name companyName
                ,e.dateStart
                ,e.category categoryName
                ,dateEnd      
                ,SEC_TO_TIME(TIMESTAMPDIFF(SECOND,dateStart,dateEnd)) AS timeSpent
                ,v.model
                ,v.licensePlate 
            from event_query e
                left join vehicle v on v.id = e."idVehicle"
                left join company c on c.id = e."idCompany"
            where dateEnd <> 0
            order by dateStart asc
                """
                
            query = text(query)
            session = Session()
            data = session.execute(query).all()
            session.close()

            return render_template('htmx/report.html',data=data)