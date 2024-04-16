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
        results = session.query(Company).filter(Company.idUser == current_user.id).all()
        session.close()
        return render_template('profile.html',current_user = current_user ,companies=results)
    
## Implement CRUD 
## Edit fields and change password
