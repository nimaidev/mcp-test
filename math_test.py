# maths.py (Example MCP Server)
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

class MathMCPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/call':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                function_name = data.get('function')
                args = data.get('args', {})
                
                result = self.execute_function(function_name, args)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                self.send_error(500, str(e))
    
    def execute_function(self, function_name, args):
        if function_name == 'add':
            a = args.get('a', 0)
            b = args.get('b', 0)
            return {"result": a + b}
        
        elif function_name == 'multiply':
            a = args.get('a', 0)
            b = args.get('b', 0)
            return {"result": a * b}
        
        elif function_name == 'divide':
            a = args.get('a', 0)
            b = args.get('b', 1)
            if b == 0:
                return {"error": "Division by zero"}
            return {"result": a / b}
        
        else:
            return {"error": f"Unknown function: {function_name}"}

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MathMCPHandler)
    print(f"MCP Math Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    run_server(port)