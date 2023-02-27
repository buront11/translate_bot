import logging
import os
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv

from translate import jp_en_translate, en_jp_translate
import json
from slack_sdk.errors import SlackApiError

# .envファイルの内容を読み込見込む
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = App()

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)
client = WebClient(os.environ["SLACK_BOT_TOKEN"])

# app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


@app.message("hello")
def message_hello(message, say):
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text":"Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )
    
@app.event("reaction_added")
def event_reactions_get(event, say):
    try:
        emoji = event["reaction"]
        if emoji != "gb" and emoji != 'jp':
            return 
        user = event["user"]
        item_user = event["item_user"]
        channel = event["item"]["channel"]
        ts = event["item"]["ts"]

        # タイムスタンプでメッセージを特定
        conversations_history = client.conversations_history(
            channel=channel, oldest=ts, latest=ts, inclusive=1
        )

        messages = conversations_history.data["messages"]

        if not messages:
            group_history = client.conversations_replies(channel=channel, ts=ts)
            messages = group_history.data["messages"]

        translate_text = messages[0]['text']
        reactions = messages[0]['reactions']

        start_en_postmessage = False
        start_jp_postmessage = False

        for r in reactions:
            name = r['name']
            count = r['count']
            if name == 'jp' and count == 1 and emoji == 'jp':
                start_en_postmessage = True
            elif name == "gb" and count == 1 and emoji == 'gb':
                start_jp_postmessage = True
        
        if not start_jp_postmessage and not start_en_postmessage:
            return

        if start_jp_postmessage:
            text = str(jp_en_translate(translate_text))
        elif start_en_postmessage:
            text = str(en_jp_translate(translate_text))

        attachments = json.dumps([
            {
                "pretext": text,
                "text": translate_text,
                "mrkdwn_in": ["text", "pretext"]
            }
        ])

        client.chat_postMessage(channel=channel, thread_ts=ts, attachments=attachments)
    
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    # SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))