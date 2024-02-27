"""Module provides a function to trigger a push notification to a web browser."""
import json
import requests
from pywebpush import webpush, WebPushException
import scope.config
from typing import Union


def trigger_push_notification(
    vapid_config: scope.config.VapidKeysConfig,
    push_subscription: dict,
    title: str,
    options: dict,
) -> str:
    """Function to trigger a push notification to a web browser."""
    try:
        subscription_info = {
            "endpoint": push_subscription["endpoint"],
            "keys": {
                "auth": push_subscription["keys"]["auth"],
                "p256dh": push_subscription["keys"]["p256dh"],
            },
        }

        response = webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "options": options}),
            vapid_private_key=vapid_config.private_key,
            vapid_claims={"sub": f"mailto:{vapid_config.claim_email}"},
        )

        return repr(response)
    except WebPushException as ex:
        return str(ex)
