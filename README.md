# OpenAI Triage Agent with Gradio Interface

This project implements a triage system using OpenAI's Assistants API with a Gradio chat interface. The system includes multiple specialized assistants (Technical Support, Customer Service, and Sales) and uses a triage assistant to route queries to the appropriate specialist.

## Features

- Triage system to categorize and route user queries
- Specialized assistants for different types of inquiries
- Real-time chat interface using Gradio
- Persistent conversation history
- Easy-to-use web interface

## Prerequisites

- Python 3.13 or higher
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd semantic-search-openai-agents-sdk
```

2. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Install dependencies:
```bash
pip install -e .
```

## Running the Application

1. Start the chat interface:
```bash
python agent_triage_chat.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (usually http://localhost:7860)

## Usage

1. Type your question or request in the text box
2. The triage assistant will analyze your query and route it to the appropriate specialist
3. You'll receive a response that includes both the triage analysis and the specialist's answer
4. Continue the conversation with the assigned specialist

## System Components

- **Triage Assistant**: Analyzes queries and routes them to specialists
- **Technical Support**: Handles technical issues and troubleshooting
- **Customer Service**: Manages general inquiries and account-related questions
- **Sales**: Handles pricing and product information requests

## Note

Make sure to keep your OpenAI API key secure and never commit it to version control.
