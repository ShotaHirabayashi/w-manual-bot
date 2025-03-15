import requests

from django.conf import settings


def notify_slack_msg(text):
    """
    slackへメッセージ送信
    """
    url = "https://slack.com/api/chat.postMessage"
    data = {
        "token": settings.SLACK_BOT_TOKEN,
        "channel": "C01TY38JN72",
        "text": text
    }
    requests.post(url, data=data)