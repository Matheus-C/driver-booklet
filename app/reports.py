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

            ## needs validation before querying
            query = f"""
            WITH event_query as 
            (SELECT e.eventTime date_start,
                    et.category,
                    case when et.name like '%_end' then 0
                    ELSE LEAD(eventTime, 1, 0) OVER (PARTITION BY et.name ORDER BY eventTime ASC) 
                    END as date_end,
                    e.idVehicle,
                    e.idCompany,
                    e.geolocation,
                    e.idAttachment
            FROM `event` e
            INNER JOIN `eventType` et ON et.id = e.idType
            WHERE idUser = {current_user.id})
        
        select 
            c.name CompanyName
            ,e.date_start
            ,e.category CategoryName
            ,date_end      
            ,TIMESTAMPDIFF(SECOND,date_start,date_end)/3600 AS timeSpent
            ,v.model
            ,v.licensePlate 
        from event_query e
        inner join vehicle v on v.idCompany = e.idCompany and e.idVehicle = v.id
        inner join company c on c.id = e.idCompany
        where date_end <> 0
            order by date_start desc
            """
            
        query = text(query)
        session = Session()
        data = session.execute(query).fetchmany(5)
        session.close()

        return render_template('htmx/report.html',data=data)