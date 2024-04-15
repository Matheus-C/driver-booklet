from flask import render_template, request, jsonify,send_file
from app.models.models import *
from app.models.database import *
from app import app
from flask_login import current_user,login_required

@app.route("/api/push-subscriptions", methods=["POST"])
@login_required
def create_push_subscription():
    if current_user:
        session = Session()
        json_data = request.get_json()
        subscription = session.query(PushSubscription).filter(
            # PushSubscription.subscription_json == json_data['subscription_json'],
            PushSubscription.userId == current_user.id
        ).first()
        if subscription is None:
            subscription = PushSubscription(
                subscription_json=json_data['subscription_json'],
                userId = current_user.id
            )
            session.add(subscription)
            session.commit()
            session.close()
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})



@app.route('/manifest.json')
def serve_manifest():
    return send_file('static/manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def service_worker():
    return send_file('static/sw.js', mimetype='application/javascript')