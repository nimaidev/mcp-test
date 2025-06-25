#!/usr/bin/env python3
"""
Web-based MCP Math Client

A Flask web application that provides a web interface to the MCP math server.
"""

from flask import Flask, render_template, request, jsonify
import asyncio
import sys
import os

# Add the current directory to the path so we can import our client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_client import MCPMathClient

app = Flask(__name__)
client = MCPMathClient()

@app.route('/')
def index():
    """Serve the main calculator page."""
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Handle calculation requests."""
    try:
        data = request.get_json()
        operation = data.get('operation')
        numbers = data.get('numbers', [])
        
        if operation == 'add' and len(numbers) == 2:
            result = asyncio.run(client.add(numbers[0], numbers[1]))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"{numbers[0]} + {numbers[1]} = {result}"
            })
        
        elif operation == 'subtract' and len(numbers) == 2:
            result = asyncio.run(client.subtract(numbers[0], numbers[1]))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"{numbers[0]} - {numbers[1]} = {result}"
            })
        
        elif operation == 'multiply' and len(numbers) == 2:
            result = asyncio.run(client.multiply(numbers[0], numbers[1]))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"{numbers[0]} × {numbers[1]} = {result}"
            })
        
        elif operation == 'divide' and len(numbers) == 2:
            result = asyncio.run(client.divide(numbers[0], numbers[1]))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"{numbers[0]} ÷ {numbers[1]} = {result}"
            })
        
        elif operation == 'power' and len(numbers) == 2:
            result = asyncio.run(client.power(numbers[0], numbers[1]))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"{numbers[0]}^{numbers[1]} = {result}"
            })
        
        elif operation == 'sqrt' and len(numbers) == 1:
            result = asyncio.run(client.square_root(numbers[0]))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"√{numbers[0]} = {result}"
            })
        
        elif operation == 'factorial' and len(numbers) == 1:
            result = asyncio.run(client.factorial(int(numbers[0])))
            return jsonify({
                'success': True, 
                'result': result,
                'expression': f"{int(numbers[0])}! = {result}"
            })
        
        else:
            return jsonify({
                'success': False, 
                'error': 'Invalid operation or wrong number of arguments'
            })
    
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })

@app.route('/tools')
def list_tools():
    """List available tools from the MCP server."""
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
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Math Calculator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .calculator {
            display: grid;
            gap: 15px;
        }
        .input-group {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        input[type="number"] {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            flex: 1;
        }
        select {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            min-width: 120px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            font-size: 18px;
            font-weight: bold;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .single-input {
            display: none;
        }
        .dual-input {
            display: flex;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧮 MCP Math Calculator</h1>
        <div class="calculator">
            <div class="input-group">
                <select id="operation" onchange="updateInputs()">
                    <option value="add">Add (+)</option>
                    <option value="subtract">Subtract (-)</option>
                    <option value="multiply">Multiply (×)</option>
                    <option value="divide">Divide (÷)</option>
                    <option value="power">Power (^)</option>
                    <option value="sqrt">Square Root (√)</option>
                    <option value="factorial">Factorial (!)</option>
                </select>
            </div>
            
            <div id="dual-inputs" class="input-group dual-input">
                <input type="number" id="num1" placeholder="First number" step="any">
                <input type="number" id="num2" placeholder="Second number" step="any">
            </div>
            
            <div id="single-input" class="input-group single-input">
                <input type="number" id="single-num" placeholder="Number" step="any">
            </div>
            
            <button onclick="calculate()">Calculate</button>
            
            <div id="result"></div>
            
            <div style="margin-top: 30px; text-align: center;">
                <button onclick="listTools()" style="background: #28a745;">List Available Tools</button>
            </div>
        </div>
    </div>

    <script>
        function updateInputs() {
            const operation = document.getElementById('operation').value;
            const dualInputs = document.getElementById('dual-inputs');
            const singleInput = document.getElementById('single-input');
            
            if (operation === 'sqrt' || operation === 'factorial') {
                dualInputs.style.display = 'none';
                singleInput.style.display = 'flex';
            } else {
                dualInputs.style.display = 'flex';
                singleInput.style.display = 'none';
            }
        }

        function calculate() {
            const operation = document.getElementById('operation').value;
            let numbers = [];
            
            if (operation === 'sqrt' || operation === 'factorial') {
                const num = parseFloat(document.getElementById('single-num').value);
                if (isNaN(num)) {
                    showResult(false, 'Please enter a valid number');
                    return;
                }
                numbers = [num];
            } else {
                const num1 = parseFloat(document.getElementById('num1').value);
                const num2 = parseFloat(document.getElementById('num2').value);
                if (isNaN(num1) || isNaN(num2)) {
                    showResult(false, 'Please enter valid numbers');
                    return;
                }
                numbers = [num1, num2];
            }
            
            fetch('/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    operation: operation,
                    numbers: numbers
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showResult(true, data.expression);
                } else {
                    showResult(false, data.error);
                }
            })
            .catch(error => {
                showResult(false, 'Connection error: ' + error);
            });
        }

        function showResult(success, message) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'result ' + (success ? 'success' : 'error');
            resultDiv.textContent = message;
        }

        function listTools() {
            fetch('/tools')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showResult(true, 'Available tools: ' + data.tools.join(', '));
                } else {
                    showResult(false, 'Error listing tools: ' + data.error);
                }
            })
            .catch(error => {
                showResult(false, 'Connection error: ' + error);
            });
        }

        // Initialize inputs
        updateInputs();
    </script>
</body>
</html>'''
    
    with open('templates/calculator.html', 'w') as f:
        f.write(html_content)
    
    print("Starting MCP Math Calculator Web Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)
