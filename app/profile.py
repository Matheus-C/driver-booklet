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
        results = session.query(User,Company).join(Company,Company.idUser == User.id,isouter=True).filter(User.id == current_user.id).all()
        session.close()
        return render_template('profile.html',user_info=results)
    
## Implement CRUD 
## Edit fields and change password
