from django.conf import settings

from linebot import LineBotApi
from linebot.models import (
    FlexSendMessage,
)

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)


# 予約確定
def send_menu_message(line_id):
    content_json = {
        "type": "flex",
        "altText": "認証パスワードが異なります。",
        "contents": {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "プロフィール変更",
                        "align": "center",
                        "contents": [],
                    }
                ],
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": "以下のボタンから変更可能です。",
                        "align": "center",
                        "contents": [],
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "プロフィール変更",
                            "uri": f"https://liff.line.me/{settings.LIFF_ID}?line_id={line_id}",
                        },
                        "style": "primary",
                    },
                ],
            },
        },
    }

    result = FlexSendMessage.new_from_json_dict(content_json)
    line_bot_api.push_message(line_id, messages=result)

