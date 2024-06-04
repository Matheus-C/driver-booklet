from flask import render_template, request
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required
from sqlalchemy.sql import text

@app.route("/overview", methods=["GET"])# travar para usuarios normais
@login_required
def overview():
    if current_user:
        if request.method == 'GET':
            session = Session()
            results = session.query(Company).filter(Company.idUser == current_user.id).all()
            session.close()
            return render_template('overview.html',companies = results)

@app.route("/overview/actual/<id>", methods=["GET"])
@login_required
def overview_actual(id):
    if current_user:
        if request.method == 'GET':
            query = f""" 
            WITH max_time AS(
                SELECT
                    e.idUser,
                    MAX(e.createdAt) AS m
                FROM
                    `event` e
                GROUP BY
                    e.idUser
            )
            SELECT
                e.idUser,
                et.category,
                e.idCompany
            FROM event
                e
            INNER JOIN max_time m ON
                m.idUser = e.idUser
            INNER JOIN `eventType` et ON
                et.id = e.idType
            WHERE
                m.m = e.createdAt and e.idCompany = {id}; """
            query = text(query)
            session = Session()
            data = session.execute(query).all()
            max = session.query(UserCompany).filter(UserCompany.idCompany == id).count()
            session.close()
            status = {"Work": 0, "Availability": 0, "Rest": 0}
            for d in data:
                if d.category == "Work":
                    status["Work"] += 1
                elif d.category == "Availability":
                    status["Availability"] += 1
                elif d.category == "Rest":
                    status["Rest"] += 1
            return render_template('htmx/employee_status.html',status = status, max = max)

@app.route("/overview/month/<id>", methods=["GET"])
@login_required
def overview_month(id):
    if current_user:
        if request.method == 'GET':
            query = f""" 
            WITH event_query as (
                SELECT idUser,
                 		e.eventTime dateStart,
                        et.category,
                        case when et.name like '%_end' then 0
                        ELSE LEAD(eventTime, 1, 0) OVER (ORDER BY eventTime ASC)
                        END as dateEnd,
                        e.idCompany
                FROM `event` e
                INNER JOIN `eventType` et ON et.id = e.idType
                WHERE e.idCompany = {id}
                and e.eventTime BETWEEN DATE_FORMAT(NOW() ,'%Y-%m-01') and LAST_DAY(NOW())
                ), max_time as (
                    select e.idUser AS idUser
                ,TIMESTAMPDIFF(SECOND,dateStart,dateEnd) AS timeSpent
            from event_query e
                left join company c on c.id = e.idCompany
            where dateEnd <> 0
            order by dateStart asc)
            SELECT SEC_TO_TIME(SUM(max_time.timeSpent)/COUNT(DISTINCT max_time.idUser)) as total FROM max_time"""
            query = text(query)
            session = Session()
            avg = session.execute(query).first().total
            session.close()
            
            return render_template('htmx/company_month.html',avg = avg)
