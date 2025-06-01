# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Import libraries
import gradio as gr
from openai import OpenAI

import json
from agents import GuardrailFunctionOutput, Agent, Runner
from find_user import find_user
from record_unknown_question import record_unknown_question_json, record_unknown_question
from students_find import agent as students_agent


# setup toos
tools = [find_user, {"type": "function", "function": record_unknown_question_json}]


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

# Define the chat function
def chat(message, history):
    if not openai_available:
        return "OpenAI client not available. Please check your .env file."
    
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]

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
 

# Launch the chat interface
gr.ChatInterface(chat, type="messages").launch()
