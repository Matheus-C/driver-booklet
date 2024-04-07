from flask import render_template, request
# from app.models import Session, distinct, extract,func
# from app.models import FlightCombinations, AirportInformation
from app import app

@app.route('/gps')
def test_gps():
    return render_template('htmx/test_gps.html')

@app.route('/notifications')
def test_notifications():
    return render_template('htmx/test_notifications.html')
