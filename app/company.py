from flask import render_template, request, jsonify,send_file, url_for
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required


@app.route("/company", methods=["GET","POST"])
@login_required
def company():
    if current_user:
        if request.method == 'GET':
            return render_template('htmx/company_add_form.html',current_user=current_user)
        elif request.method == 'POST' and request.form:
            dict_data = request.form.to_dict()
            dict_data['idUser'] = current_user.id
            company = Company(**dict_data)
            session = Session()
            session.add(company)
            session.commit()
            session.close()
            return url_for('/profile')
        
@app.route("/company/<id>", methods=["GET","POST"])
@login_required
def company_info(id):
    if current_user:
        if request.method == 'GET':
            session = Session()
            results = session.query(Company,UserCompany,User)\
            .join(UserCompany,UserCompany.idCompany == Company.id,isouter=True)\
            .join(User,UserCompany.idCompany == User.id,isouter=True)\
            .filter(Company.idUser == current_user.id,Company.id == id).all()
            return render_template('company.html',company_info = results,current_user=current_user)
        elif request.method == 'POST' and request.form:
            dict_data = request.form.to_dict()
            dict_data['idUser'] = current_user.id
            company = Company(**dict_data)
            session = Session()
            session.add(company)
            session.commit()
            session.close()
            return url_for('/profile')