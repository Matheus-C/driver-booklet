from app.models.models import *
from flask import Flask, redirect
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from app.models import *  # importing db + models
from flask_apscheduler import APScheduler
import flask_admin
from flask_babel import Babel  # necessary to flask_admin
from dotenv import load_dotenv

app = Flask(__name__)

babel = Babel(app)  # necessary to flask_admin

load_dotenv()


app.secret_key = os.environ.get('secret_key')

app.config[
    'VAPID_PUBLIC_KEY'] = os.environ.get('vapid_public_key')

app.config['VAPID_PRIVATE_KEY'] = os.environ.get('vapid_private_key')

app.config['VAPID_CLAIM_EMAIL'] = "a@a.com"

app.config['TRAP_HTTP_EXCEPTIONS'] = True

app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('security_password_salt')

# mail settings
app.config["MAIL_SERVER"] = os.environ.get('mail_server')
app.config["MAIL_PORT"] = os.environ.get('mail_port')
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

# mail authentication
app.config["MAIL_USERNAME"] = os.environ.get('mail_username')
app.config["MAIL_PASSWORD"] = os.environ.get('mail_password')

# mail accounts
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get('mail_username')

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
