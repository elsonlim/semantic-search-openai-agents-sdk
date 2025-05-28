# Import libraries
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
import requests
import json
import os

load_dotenv(override=True)

# Setup push notification
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"2. Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)
    return {"recorded": "ok"}

# Setup Semantic Search Tool
userDB = [{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "notes": "John Doe is a software engineer at Google"
}, {
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "notes": "Jane Smith is a software engineer at Apple"
}]

def find_user(name):
    print(f"2. Searching: {name}")
    for user in userDB:
        if user["name"].lower() == name.lower():
            return str(user)
    return f"No user of {name} found"

find_user_json = {
    "name": "find_user",
    "description": "Always use this tool to find a user in the user database",
    "parameters": {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "The name of the user to find"}},
        "required": ["name"],
        "additionalProperties": False
    }
}

# record_user_query_tool
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

# setup toos
tools = [{"type": "function", "function": find_user_json},
        {"type": "function", "function": record_unknown_question_json}]


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name} with arugements: {arguments}", flush=True)
        tool = globals().get(tool_name) # using globals, we can remove the IF statement
        result = tool(**arguments) if tool else {}
        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results
    
# Setup Prompt
system_prompt = f""""
You are a helpful chat assistant.
when 
- find_user: Find a user in the user database
- record_unknown_question: Record that a user asked a question that you couldn't answer

You will always use the find_user tool to find a user in the user database.
You will always use the record_unknown_question tool to record that a user asked a question that you couldn't answer.
"""

# Setup open AI
try:
    client = OpenAI()
    openai_available = True
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Please ensure your OPENAI_API_KEY is set correctly in your .env file.")
    openai_available = False


def chat(message, history):
    if not openai_available:
        return "OpenAI client not available. Please check your .env file."
    
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    done = False
    while not done:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
        except client.APIError as e:
            print(f"OpenAI API Error: {e}")
            return f"Sorry, there was an error communicating with the AI: {e}"

        finish_reason = response.choices[0].finish_reason
         
        if finish_reason=="tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.content
 


gr.ChatInterface(chat, type="messages").launch()
