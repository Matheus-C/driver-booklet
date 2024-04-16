from flask import render_template, request, jsonify,send_file, url_for
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required



@app.route("/profile", methods=["GET"])
@login_required
def profile():
    if current_user:
        session = Session()
        results = session.query(User,Company).join(Company,Company.idUser == User.id).filter(User.id == current_user.id).all()
        session.close()
        return render_template('profile.html',user_info=results)
    
## Implement CRUD 
## Edit fields and change password


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