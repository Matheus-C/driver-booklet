from flask import render_template
from flask_login import current_user, login_required

from app import app
from app.models.models import *


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    if current_user:
        session = Session()
        results = session.query(Company) \
            .join(UserCompany, UserCompany.idCompany == Company.id, isouter=True) \
            .filter(UserCompany.idUser == current_user.id,
                    UserCompany.validUntil == None).all()
        session.close()
        return render_template('profile.html', current_user=current_user, companies=results)

# Implement CRUD
# Edit fields and change password
