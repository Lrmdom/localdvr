import json
import os
import logging
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, subscription_file="subscriptions.json"):
        self.subscription_file = subscription_file
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
        self.vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
        self.vapid_claims = {"sub": "mailto:admin@localdvr.local"}
        
        if not self.vapid_private_key or not self.vapid_public_key:
            logger.warning("VAPID keys not configured. Push notifications will not work.")

    def get_subscriptions(self):
        if not os.path.exists(self.subscription_file):
            return []
        with open(self.subscription_file, "r") as f:
            return json.load(f)

    def save_subscription(self, subscription):
        subs = self.get_subscriptions()
        if subscription not in subs:
            subs.append(subscription)
            with open(self.subscription_file, "w") as f:
                json.dump(subs, f)

    def send_notification(self, title, body, data=None):
        if not self.vapid_private_key or not self.vapid_public_key:
            return

        payload = {
            "title": title,
            "body": body,
            "data": data
        }
        
        for sub in self.get_subscriptions():
            try:
                webpush(
                    subscription_info=sub,
                    data=json.dumps(payload),
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims
                )
                logger.info(f"Push enviado: {title}")
            except WebPushException as e:
                logger.error(f"Erro ao enviar push: {e}")
