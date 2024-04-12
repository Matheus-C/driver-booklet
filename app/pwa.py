from flask import render_template, request, jsonify,send_file
from app.models.models import *
from app.models.database import *
from app import app

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


@app.route('/manifest.json')
def serve_manifest():
    return send_file('static/manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def service_worker():
    return send_file('static/sw.js', mimetype='application/javascript')