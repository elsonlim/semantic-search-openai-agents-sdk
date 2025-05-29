import os
import requests

# Setup push notification
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"2. Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)
    return {"recorded": "ok"}

def record_unknown_question(question):
    push(f"2. Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record that a user asked a question that you couldn't answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that the user asked"
            }
        },
        "required": ["question"],
        "additionalProperties": False
    }
}