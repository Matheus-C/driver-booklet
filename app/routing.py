from flask import render_template
from app import app
from flask_login import current_user,login_required

@app.route("/blank", methods=["GET"])
def blank():
    return render_template('htmx/blank.html')
    
