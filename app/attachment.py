from flask import render_template, request, jsonify,send_file,redirect
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import login_required,current_user
from datetime import datetime
from sqlalchemy.sql import text


@app.route("/attachment/new", methods=['GET', 'POST'])
@login_required
def new_attachment():
    if current_user:
        if request.method == 'GET':
            return render_template('new_attachment.html', current_user=current_user)