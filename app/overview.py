from flask import render_template, request, url_for, redirect,jsonify, flash
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required
from sqlalchemy.sql import text

@app.route("/overview", methods=["GET"])
@login_required
def overview():
    if current_user:
        if request.method == 'GET':
            session = Session()
            results = session.query(Company).filter(Company.idUser == current_user.id).all()
            session.close()
            return render_template('overview.html',companies = results)