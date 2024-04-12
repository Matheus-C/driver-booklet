from flask import Flask

# importing db + models
from app.models import *

app = Flask(__name__)

# import views

from app import routing

from app import timer