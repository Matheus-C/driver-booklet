from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.models import * # importing db + models

app = Flask(__name__)
app.secret_key = 'ousadiaealegria'

app.config['VAPID_PUBLIC_KEY'] = "BIQgErEfMAg3DSMCy85_kHVgE9uS3NSb5Rl4pmXPknmbrd4CvdvTMUwZ8K2RUxE2_6KkKh3VYG1tLaFRXiGURxA"

app.config['VAPID_PRIVATE_KEY'] = "LXemf14HHkxNVXhsZOnn1nCcCUpI68pFSjtNRPKUIc4"

app.config['VAPID_CLAIM_EMAIL'] = "a@a.com"

login_manager = LoginManager()
login_manager.init_app(app)


bcrypt = Bcrypt(app)

from app import auth, profile, pwa, timer, company, routing, vehicle, reports
