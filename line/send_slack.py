import requests

from django.conf import settings


def notify_slack_msg(text):
    """
    slackへメッセージ送信
    """
    url = "https://slack.com/api/chat.postMessage"
    data = {
        "token": settings.SLACK_BOT_TOKEN,
        "channel": "C08HWQTPS9H",
        "text": text
    }
    requests.post(url, data=data)