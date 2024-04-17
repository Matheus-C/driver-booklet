from flask import render_template, request, url_for, redirect
from app.models.models import *
from app.models.database import *
from app import app,bcrypt
from flask_login import current_user,login_required

        
@app.route('/vehicle_add/<id_company>',methods=['GET','POST'])
def vehicle_add(id_company=None):
    if request.method == 'GET':
        return render_template('htmx/vehicle_add_form.html',data={'return':f'/vehicle_add/{id_company}'})
    
    elif request.method == 'POST' and request.form:
        dict_data = request.form.to_dict()
        dict_data['idCompany'] = id_company
        vehicle = Vehicle(**dict_data)
        session = Session()
        session.add(vehicle)
        session.commit()

        return redirect(f'/company/{id_company}')