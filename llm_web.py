#!/usr/bin/env python3
"""
LLM Web Interface for MCP Math Client

A Flask web application that provides a chat interface for natural language math queries.
"""

from flask import Flask, render_template, request, jsonify
import asyncio
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_client import LLMMathClient

app = Flask(__name__)
client = LLMMathClient()

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            })
        
        # Process the message with LLM
        response = asyncio.run(client.process_natural_language(message))
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/tools')
def list_tools():
    """List available tools."""
    try:
        asyncio.run(client.connect_and_discover())
        return jsonify({
            'success': True,
            'tools': list(client.available_tools.keys())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Create templates directory and HTML file
    os.makedirs('templates', exist_ok=True)
    
    chat_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Math Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }

        .message.user {
            flex-direction: row-reverse;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .message.assistant .message-content {
            background: white;
            border: 1px solid #e0e0e0;
            color: #333;
        }

        .message-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: #667eea;
            color: white;
        }

        .message.assistant .message-avatar {
            background: #28a745;
            color: white;
        }

        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }

        .input-group {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .input-field {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            resize: none;
            max-height: 100px;
            min-height: 50px;
        }

        .input-field:focus {
            outline: none;
            border-color: #667eea;
        }

        .send-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            transition: transform 0.2s;
        }

        .send-button:hover {
            transform: scale(1.1);
        }

        .send-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 10px;
            color: #666;
            font-style: italic;
        }

        .examples {
            margin: 20px 0;
            padding: 15px;
            background: #f0f8ff;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .examples h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .examples ul {
            list-style: none;
            padding: 0;
        }

        .examples li {
            margin: 5px 0;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 5px;
            transition: background 0.2s;
        }

        .examples li:hover {
            background: rgba(102, 126, 234, 0.1);
        }

        .error {
            background: #f8d7da !important;
            color: #721c24 !important;
            border-color: #f5c6cb !important;
        }

        @media (max-width: 600px) {
            .container {
                width: 95%;
                height: 90vh;
            }
            
            .message-content {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 LLM Math Assistant</h1>
            <p>Ask me anything about math in natural language!</p>
        </div>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message assistant">
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">
                        Hi! I'm your AI math assistant. I can help you with calculations using natural language. Try asking me something like "What's 15 plus 25?" or "Calculate the square root of 144".
                    </div>
                </div>
                
                <div class="examples">
                    <h3>Try these examples:</h3>
                    <ul>
                        <li onclick="setMessage('What\\'s 15 plus 25 times 2?')">• "What's 15 plus 25 times 2?"</li>
                        <li onclick="setMessage('Calculate the square root of 144')">• "Calculate the square root of 144"</li>
                        <li onclick="setMessage('What\\'s 5 factorial?')">• "What's 5 factorial?"</li>
                        <li onclick="setMessage('Raise 2 to the power of 8')">• "Raise 2 to the power of 8"</li>
                        <li onclick="setMessage('What\\'s 100 divided by 4?')">• "What's 100 divided by 4?"</li>
                    </ul>
                </div>
            </div>
            
            <div class="loading" id="loading">
                🤖 Thinking and calculating...
            </div>
            
            <div class="input-container">
                <div class="input-group">
                    <textarea 
                        id="messageInput" 
                        class="input-field" 
                        placeholder="Ask me a math question..."
                        rows="1"
                        onkeypress="handleKeyPress(event)"
                    ></textarea>
                    <button class="send-button" onclick="sendMessage()" id="sendButton">
                        ➤
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function addMessage(content, isUser = false, isError = false) {
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = isUser ? '👤' : '🤖';
            
            const messageContent = document.createElement('div');
            messageContent.className = `message-content ${isError ? 'error' : ''}`;
            messageContent.textContent = content;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function setLoading(loading) {
            document.getElementById('loading').style.display = loading ? 'block' : 'none';
            document.getElementById('sendButton').disabled = loading;
            document.getElementById('messageInput').disabled = loading;
        }
        
        function setMessage(message) {
            document.getElementById('messageInput').value = message;
            document.getElementById('messageInput').focus();
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            input.value = '';
            
            // Show loading
            setLoading(true);
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addMessage(data.response);
                } else {
                    addMessage(`Error: ${data.error}`, false, true);
                }
            } catch (error) {
                addMessage(`Connection error: ${error.message}`, false, true);
            } finally {
                setLoading(false);
                input.focus();
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        // Auto-resize textarea
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
        
        // Focus input on load
        window.onload = function() {
            document.getElementById('messageInput').focus();
        };
    </script>
</body>
</html>'''
    
    with open('templates/chat.html', 'w') as f:
        f.write(chat_html)
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    print("🧠 Starting LLM Math Assistant Web Server...")
    print("🌐 Open http://localhost:5001 in your browser")
    print("💡 Ask natural language math questions like:")
    print("   • 'What's 15 plus 25?'")
    print("   • 'Calculate the square root of 144'")
    print("   • 'What's 5 factorial?'")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
