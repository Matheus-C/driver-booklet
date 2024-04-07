from flask import render_template, request, jsonify
from app.models.models import *
from app.models.database import *
from app import app
import json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gps')
def gps():
    return render_template('htmx/test_gps.html')

@app.route('/notifications')
def notifications():
    return render_template('htmx/test_notifications.html')

@app.route('/notificationssw')
def notificationsSW():
    return render_template('htmx/test_notifications_w_sw.html')

@app.route("/api/push-subscriptions", methods=["POST"])
def create_push_subscription():
    session = Session()
    json_data = request.get_json()
    PushSubscription
    subscription = session.query(PushSubscription).filter(
        PushSubscription.subscription_json == json_data['subscription_json']
    ).first()
    if subscription is None:
        subscription = PushSubscription(
            subscription_json=json_data['subscription_json']
        )
        session.add(subscription)
        session.commit()
    return jsonify({"status": "success"})
