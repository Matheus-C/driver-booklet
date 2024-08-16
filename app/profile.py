from app.email import *
from flask import render_template, request, redirect, url_for, flash
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


@app.route("/profile/data", methods=["GET"])
@login_required
def profile_data():
    return render_template("htmx/profile/user_data.html", current_user=current_user)


@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user and request.method == 'GET':
        return render_template("htmx/profile/edit_profile.html", current_user=current_user)
    elif request.form and request.method == 'POST':
        session = Session()
        user = session.query(User).filter(User.id == current_user.id).first()
        if request.form["name"] != "":
            user.__setattr__("name", request.form["name"])
        if request.form["phone"] != "":
            user.__setattr__("phone", request.form["phone"])
        if request.form["address"] != "":
            user.__setattr__("address", request.form["address"])
        if request.form["birthDate"] != "":
            user.__setattr__("birthDate", request.form["birthDate"])
        session.add(user)
        session.commit()
        session.close()
        flash("Alteração bem sucedida", "success")
        return redirect("/profile/data")


@app.route("/profile/change_password", methods=["GET"])
@login_required
def change_password():
    if request.method == "GET" and current_user:
        token = generate_confirmation_token(current_user.email)
        url = url_for('new_password', token=token, _external=True)
        msg = "Clique no link abaixo para redefinir sua senha:"
        html = render_template('email/email_template.html', url=url, msg=msg)
        subject = "Redefinição de senha"
        send_email(current_user.email, subject, html)
        flash("Foi enviado um Email contendo um link para a redefinição da senha.", "success")
        return render_template('base/notifications.html')

