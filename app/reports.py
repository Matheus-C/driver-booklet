from flask import render_template, request, url_for, redirect
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required


@app.route("/reports", methods=["GET","POST"])
@login_required
def reports():
    if current_user:
        if request.method == 'GET':
            return render_template('reports.html',current_user=current_user)
        
        if request.method == 'POST':
            # get companies, that you worked for and cars ?
            session = Session()
            
            return 'pass'

            

