from flask import render_template, request, jsonify,send_file
from app.models.models import *
from app.models.database import *
from app import app


@app.route('/timer')
# @login.required
def timer():
    return render_template('htmx/timer.html')
