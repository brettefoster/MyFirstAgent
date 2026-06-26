#!/usr/bin/env python3
"""
Example solution for Stage 8 Exercise 3: Build a Web Interface

This script demonstrates creating a simple web UI for the agent using Flask.
It displays streaming responses in real-time and shows tool call status.
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path so we can import utils
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Import central configuration and API client
from utils.config import config
from utils.api_client import APIClient, create_payload
from utils.formatter import Formatter

try:
    from flask import Flask, render_template_string, request, jsonify, Response
except ImportError:
    Flask = None


# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My First Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
            background-color: #1a1a2e;
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background-color: #16213e;
            padding: 16px 24px;
            border-bottom: 2px solid #0f3460;
        }

        .header h1 {
            color: #e94560;
            font-size: 1.5rem;
        }

        .chat-container {
            flex: 1;
            max-width: 900px;
            margin: 20px auto;
            padding: 0 20px;
            width: 100%;
            overflow-y: auto;
        }

        .message {
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 8px;
        }

        .message.user {
            background-color: #16213e;
            border-left: 3px solid #0f3460;
        }

        .message.agent {
            background-color: #1a1a3e;
            border-left: 3px solid #e94560;
        }

        .message.tool-call {
            background-color: #0d1b2a;
            border-left: 3px solid #f0a500;
            font-family: monospace;
            font-size: 0.9rem;
        }

        .message.tool-result {
            background-color: #0d1b2a;
            border-left: 3px solid #4ecca3;
            font-family: monospace;
            font-size: 0.85rem;
            max-height: 150px;
            overflow-y: auto;
        }

        .message-label {
            font-weight: bold;
            margin-bottom: 4px;
            color: #a0a0c0;
        }

        .message-content {
            white-space: pre-wrap;
            line-height: 1.5;
        }

        .input-container {
            position: sticky;
            bottom: 0;
            background-color: #16213e;
            padding: 16px 24px;
            border-top: 2px solid #0f3460;
        }

        .input-form {
            display: flex;
            gap: 10px;
            max-width: 900px;
            margin: 0 auto;
        }

        .input-form input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #0f3460;
            border-radius: 8px;
            background-color: #1a1a2e;
            color: #e0e0e0;
            font-size: 1rem;
            outline: none;
        }

        .input-form input:focus {
            border-color: #e94560;
        }

        .input-form button {
            padding: 12px 24px;
            background-color: #e94560;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .input-form button:hover {
            background-color: #c73650;
        }

        .input-form button:disabled {
            background-color: #4a4a6a;
            cursor: not-allowed;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-indicator.thinking {
            background-color: #f0a500;
            animation: pulse 1s infinite;
        }

        .status-indicator.done {
            background-color: #4ecca3;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        .clear-btn {
            background: none;
            border: 1px solid #4a4a6a;
            color: #a0a0c0;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8rem;
        }

        .clear-btn:hover {
            border-color: #e94560;
            color: #e94560;
        }

        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-row">
            <h1>My First Agent</h1>
            <button class="clear-btn" onclick="clearChat()">Clear Chat</button>
        </div>
    </div>

    <div class="chat-container" id="chat-container">
        <div class="message agent">
            <div class="message-label">Agent</div>
            <div class="message-content">Hello! How can I help you today?</div>
        </div>
    </div>

    <div class="input-container">
        <form class="input-form" onsubmit="sendMessage(event)">
            <input type="text" id="user-input" placeholder="Type your message..." autofocus>
            <button type="submit" id="send-btn">Send</button>
        </form>
    </div>

    <script>
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        function addMessage(role, content, type = 'text') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;

            const labelDiv = document.createElement('div');
            labelDiv.className = 'message-label';
            labelDiv.textContent = role === 'user' ? 'USER' : 
                                   type === 'tool-call' ? `TOOL: ${content.name || ''}` :
                                   type === 'tool-result' ? `RESULT: ${content.name || ''}` : 'AGENT';

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';

            if (type === 'tool-call') {
                contentDiv.textContent = `${content.name}(${JSON.stringify(content.args || {})})`;
            } else if (type === 'tool-result') {
                contentDiv.textContent = typeof content.result === 'string' ? content.result : JSON.stringify(content.result, null, 2);
            } else {
                contentDiv.textContent = content;
            }

            messageDiv.appendChild(labelDiv);
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }

        function addThinkingIndicator() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message agent';
            messageDiv.id = 'thinking-indicator';

            const labelDiv = document.createElement('div');
            labelDiv.className = 'message-label';
            labelDiv.innerHTML = '<span class="status-indicator thinking"></span>AGENT (thinking...)';

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.id = 'thinking-text';
            contentDiv.textContent = '';

            messageDiv.appendChild(labelDiv);
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }

        function updateThinking(text) {
            const thinkingText = document.getElementById('thinking-text');
            if (thinkingText) {
                thinkingText.textContent = text;
            }
        }

        function removeThinkingIndicator() {
            const indicator = document.getElementById('thinking-indicator');
            if (indicator) {
                indicator.remove();
            }
        }

        async function sendMessage(event) {
            event.preventDefault();
            const message = userInput.value.trim();
            if (!message) return;

            userInput.value = '';
            sendBtn.disabled = true;

            addMessage('user', message);
            const thinking = addThinkingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                removeThinkingIndicator();

                if (data.tool_calls) {
                    data.tool_calls.forEach(tc => {
                        addMessage('tool', tc, 'tool-call');
                    });
                }

                if (data.tool_results) {
                    data.tool_results.forEach(tr => {
                        addMessage('tool', tr, 'tool-result');
                    });
                }

                if (data.content) {
                    addMessage('agent', data.content);
                }

                if (data.error) {
                    addMessage('agent', `[Error: ${data.error}]`);
                }
            } catch (error) {
                removeThinkingIndicator();
                addMessage('agent', `[Error: ${error.message}]`);
            }

            sendBtn.disabled = false;
            userInput.focus();
        }

        function clearChat() {
            const messages = chatContainer.querySelectorAll('.message');
            messages.forEach(msg => msg.remove());
            addMessage('agent', 'Chat cleared. How can I help?');
        }

        // Allow Enter key to send
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(e);
            }
        });
    </script>
</body>
</html>
"""


def create_flask_app():
    """
    Create a Flask application with the agent integrated.
    
    Returns:
        Flask app instance or None if Flask is not installed.
    """
    if Flask is None:
        print("ERROR: Flask is not installed.")
        print("Install with: pip install flask")
        return None

    app = Flask(__name__)

    # Load configuration
    base_url = config.api_base
    model = config.model
    api_key = config.api_key

    # Create API client
    client = APIClient(base_url=base_url, model=model, api_key=api_key)

    # Define tools
    tools = [
        {
            "name": "search",
            "description": "Search for information on the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "get_weather",
            "description": "Get weather information for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_time",
            "description": "Get the current time for a timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The IANA timezone name"
                    }
                },
                "required": ["timezone"]
            }
        },
        {
            "name": "calculate",
            "description": "Perform a mathematical calculation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A mathematical expression"
                    }
                },
                "required": ["expression"]
            }
        }
    ]

    # Conversation history
    conversations = {}

    def execute_tool(name, arguments):
        """Execute a tool and return the result."""
        args = json.loads(arguments) if isinstance(arguments, str) else arguments

        if name == "search":
            return f"Search results for '{args.get('query', '')}':\\n- Result 1: Information about {args.get('query', '')}\\n- Result 2: More details\\n- Result 3: Related topics"
        elif name == "get_weather":
            location = args.get("location", "unknown")
            return f"Weather in {location}: 15°C, partly cloudy, 20% chance of rain"
        elif name == "get_time":
            from datetime import datetime
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif name == "calculate":
            import ast
            import operator
            expression = args.get("expression", "")
            try:
                safe_ops = {
                    ast.Add: operator.add,
                    ast.Sub: operator.sub,
                    ast.Mult: operator.mul,
                    ast.Div: operator.truediv,
                    ast.Pow: operator.pow,
                }
                tree = ast.parse(expression, mode="eval")
                def eval_node(node):
                    if isinstance(node, ast.Num):
                        return node.n
                    elif isinstance(node, ast.BinOp):
                        left = eval_node(node.left)
                        right = eval_node(node.right)
                        return safe_ops[type(node.op)](left, right)
                    elif isinstance(node, ast.UnaryOp):
                        if isinstance(node.op, ast.USub):
                            return -eval_node(node.operand)
                        return eval_node(node.operand)
                result = eval_node(tree.body)
                return f"Result: {result}"
            except Exception as e:
                return f"Error: {e}"
        else:
            return f"Unknown tool: {name}"

    @app.route('/')
    def index():
        """Serve the main web interface."""
        return render_template_string(HTML_TEMPLATE)

    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat requests and return agent responses."""
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'Empty message'})

        # Get or create conversation history
        conv_id = data.get('conversation_id', 'default')
        if conv_id not in conversations:
            conversations[conv_id] = [
                {"role": "system", "content": "You are a helpful assistant. Call tools when needed."}
            ]

        # Add user message
        conversations[conv_id].append({"role": "user", "content": user_message})

        # Build payload
        payload = create_payload(
            messages=conversations[conv_id],
            tools=tools,
            temperature=0.7,
        )

        # Stream response
        full_response = ""
        tool_calls = []
        tool_results = []

        for chunk in client.stream(payload):
            if chunk:
                choice = chunk.get("choices", [{}])[0]
                delta = choice.get("delta", {})

                if "content" in delta and delta["content"]:
                    full_response += delta["content"]
                elif "tool_calls" in delta and delta["tool_calls"]:
                    tc = delta["tool_calls"][0]
                    if tc.get("function"):
                        func = tc["function"]
                        call_name = func.get("name", "")
                        call_args = func.get("arguments", "{}")

                        # Track tool call
                        call_info = {
                            "name": call_name,
                            "args": call_args
                        }
                        if not any(c["name"] == call_name for c in tool_calls):
                            tool_calls.append(call_info)

                        # Execute tool
                        result = execute_tool(call_name, call_args)
                        tool_results.append({
                            "name": call_name,
                            "result": result
                        })

        # Add assistant response to conversation
        if full_response:
            conversations[conv_id].append({"role": "assistant", "content": full_response})

        return jsonify({
            'content': full_response,
            'tool_calls': tool_calls,
            'tool_results': tool_results,
            'conversation_id': conv_id
        })

    return app


def demo_web_interface():
    """Demonstrate the web interface by starting the Flask server."""
    f = Formatter(show_raw=True)

    f.header("STAGE 8 EXERCISE 3: BUILD A WEB INTERFACE")
    f.script("Creating a Web UI for the Agent")
    f.print()

    f.script("  This exercise creates a Flask-based web interface that:")
    f.script("  - Displays user messages, agent responses, and tool calls")
    f.script("  - Shows tool call status in real-time")
    f.script("  - Maintains conversation history")
    f.script("  - Provides a clean, modern dark-themed UI")
    f.print()

    app = create_flask_app()

    if app is None:
        f.error("Flask is not installed. Install with: pip install flask")
        return

    f.script("  Starting Flask server...")
    f.script("  Open http://localhost:5555 in your browser")
    f.script("  Press Ctrl+C to stop the server")
    f.print()

    # Note: In a real demo, this would start the server
    # For this example, we just show how to set it up
    try:
        app.run(host='0.0.0.0', port=5555, debug=False)
    except KeyboardInterrupt:
        f.script("  Server stopped.")


if __name__ == "__main__":
    demo_web_interface()