from app.models.models import *
from flask import Flask, redirect
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from app.models import *  # importing db + models
from flask_apscheduler import APScheduler
import flask_admin
from flask_babel import Babel  # necessary to flask_admin

app = Flask(__name__)

babel = Babel(app)  # necessary to flask_admin
app.secret_key = 'ousadiaealegria'

app.config[
    'VAPID_PUBLIC_KEY'] = "BIQgErEfMAg3DSMCy85_kHVgE9uS3NSb5Rl4pmXPknmbrd4CvdvTMUwZ8K2RUxE2_6KkKh3VYG1tLaFRXiGURxA"

app.config['VAPID_PRIVATE_KEY'] = "LXemf14HHkxNVXhsZOnn1nCcCUpI68pFSjtNRPKUIc4"

app.config['VAPID_CLAIM_EMAIL'] = "a@a.com"

app.config['TRAP_HTTP_EXCEPTIONS'] = True

app.config['SECURITY_PASSWORD_SALT'] = "temperro"

# mail settings
app.config["MAIL_SERVER"] = 'smtp.mailersend.net'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

# gmail authentication
app.config["MAIL_USERNAME"] = "MS_aQ1BS4@trial-yzkq340o0yk4d796.mlsender.net"
app.config["MAIL_PASSWORD"] = "esrTpO2Zum9e6aYp"

# mail accounts
app.config["MAIL_DEFAULT_SENDER"] = 'MS_aQ1BS4@trial-yzkq340o0yk4d796.mlsender.net'

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

# initialize scheduler
scheduler = APScheduler()
# if you don't want to use a config, you can set options here:
scheduler.api_enabled = True
scheduler.init_app(app)


class MyAdminIndexView(flask_admin.AdminIndexView):
    @flask_admin.expose('/')
    def index(self):
        if not (current_user.is_authenticated and current_user.userTypeId == 3):
            return redirect('/')
        return super(MyAdminIndexView, self).index()


# Create admin
adm = flask_admin.Admin(app, index_view=MyAdminIndexView(name='Home', template='admin/index.html', url='/admin'))

from app import auth, profile, pwa, timer, company, routing, vehicle, reports, jobs, attachment, admin, error

scheduler.start()
