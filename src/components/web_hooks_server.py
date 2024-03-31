from flask import Flask, request, jsonify
from components.slack_integration import SlackIntegration
from components.ai_agent import AIAgent
from events.web_hook import WebHookEvent, WebHookEventType

app = Flask(__name__)

def badRequest(error: str):
    return jsonify({"error": error}), 400

class WebhooksServer:
    def __init__(self):
        self.app = app

    def start(self):
        self.app.run(debug=True, port=5000)

@app.route("/slack/events", methods=["POST"])
def handle_slack_web_hook():
    if not request.is_json:
        return badRequest("Request must contain JSON data.")

    data = request.get_json()

    if 'message' not in data:
        return badRequest("JSON data must contain a 'message' attribute.")

    slackIntegration = SlackIntegration()

    slackIntegration.subscribe(AIAgent())

    slackIntegration.processWebHookEvent(WebHookEvent(WebHookEventType.SLACK, "znas@znas.io", data["message"]))

    return jsonify({
        "message": "success"
    }), 200
