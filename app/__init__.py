from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.models import * # importing db + models

app = Flask(__name__)
app.secret_key = 'ousadiaealegria'

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

from app import auth, routing