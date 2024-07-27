import json

from flask import request, jsonify, send_file, current_app
from flask_login import current_user, login_required
from pywebpush import webpush, WebPushException

from app import app
from app.models.models import *


@app.route("/api/push-subscriptions", methods=["POST"])
@login_required
def create_push_subscription():
    if current_user:
        session = Session()
        json_data = request.get_json()
        subscription = session.query(PushSubscription).filter(
            PushSubscription.subscription_json == json_data['subscription_json'],
            PushSubscription.userId == current_user.id
        ).first()
        print(subscription)
        if subscription is None:
            subscription = PushSubscription(
                subscription_json=json_data['subscription_json'],
                userId=current_user.id
            )
            session.add(subscription)
            session.commit()
            session.close()
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})


@app.route("/api/update-subscription", methods=["POST"])
@login_required
def update_push_subscription():
    if current_user:
        session = Session()
        json_data = request.get_json()
        subscription = session.query(PushSubscription).filter(
            PushSubscription.subscription_json == json_data['old_endpoint']
        ).first()
        if subscription:
            subscription.subscription_json = json_data['new_endpoint']
            session.commit()
            session.close()
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})


# default function to trigger notifications with routing
@app.route("/admin-api/trigger-push-notifications", methods=["POST"])
def trigger_push_notifications():
    json_data = request.get_json()
    session = Session()
    subscriptions = session.query(PushSubscription).filter(PushSubscription.userId == current_user.id).all()
    results = trigger_push_notifications_for_subscriptions(
        subscriptions,
        json_data.get('title'),
        json_data.get('body')
    )
    return jsonify({
        "status": "success",
        "result": results
    })


# default function to trigger notifications without routing
def trigger_notifications(subscriptions, title, body):
    results = []
    for subscription in subscriptions:
        results.append(trigger_push_notification(subscription, title, body))


def trigger_push_notifications_for_subscriptions(subscriptions, title, body):
    return [trigger_push_notification(subscription, title, body)
            for subscription in subscriptions]


def trigger_push_notification(push_subscription, title, body):
    try:
        with app.app_context():
            response = webpush(
                subscription_info=json.loads(push_subscription.subscription_json),
                data=json.dumps({"title": title, "body": body}),
                vapid_private_key=current_app.config["VAPID_PRIVATE_KEY"],
                vapid_claims={
                    "sub": "mailto:{}".format(
                        current_app.config["VAPID_CLAIM_EMAIL"])
                }
            )
        return response.ok
    except WebPushException as ex:
        if ex.response and ex.response.json():
            extra = ex.response.json()
            print("Remote service replied with a {}:{}, {}",
                  extra.code,
                  extra.errno,
                  extra.message
                  )
        return False


@app.route('/manifest.json')
def serve_manifest():
    return send_file('static/manifest.json', mimetype='application/manifest+json')


@app.route('/sw.js')
def service_worker():
    return send_file('static/sw.js', mimetype='application/javascript')


@app.route('/.well-known/assetlinks.json')
def serve_assetlinks():
    return send_file('static/assetlinks.json', mimetype='application/javascript')
