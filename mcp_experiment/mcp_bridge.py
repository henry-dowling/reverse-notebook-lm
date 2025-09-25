
import asyncio
import json
import sys
import uuid
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import (
    list_scripts, get_script, load_script, get_script_progress,
    advance_script_stage, reset_script, clear_script,
    read_file, write_file, append_file, list_files,
    get_file_info, create_file, create_backup
)

class MCPBridgeHandler(BaseHTTPRequestHandler):
    def _send_jsonrpc_response(self, request_id, result=None, error=None):
        """Send a proper JSON-RPC response"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if error:
            response["error"] = {
                "code": -32603,
                "message": str(error)
            }
        else:
            response["result"] = result
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "type": "mcp_bridge"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            # Handle JSON-RPC protocol
            if "jsonrpc" in data and data["jsonrpc"] == "2.0":
                request_id = data.get("id", str(uuid.uuid4()))
                method = data.get("method")
                params = data.get("params", {})
                
                # Map MCP methods to our functions
                method_mapping = {
                    "tools/list": lambda: {"tools": [
                        {"name": "list_scripts", "description": "List all available scripts"},
                        {"name": "get_script", "description": "Get script details"},
                        {"name": "load_script", "description": "Load a script"},
                        {"name": "get_script_progress", "description": "Get script progress"},
                        {"name": "advance_script_stage", "description": "Advance script stage"},
                        {"name": "reset_script", "description": "Reset script"},
                        {"name": "clear_script", "description": "Clear script"},
                        {"name": "read_file", "description": "Read file"},
                        {"name": "write_file", "description": "Write file"},
                        {"name": "append_file", "description": "Append to file"},
                        {"name": "list_files", "description": "List files"},
                        {"name": "get_file_info", "description": "Get file info"},
                        {"name": "create_file", "description": "Create file"},
                        {"name": "create_backup", "description": "Create backup"}
                    ]},
                    "tools/call": lambda: self._call_tool(params.get("name"), params.get("arguments", {})),
                    "resources/list": lambda: {"resources": [
                        {"uri": "scripts://list", "name": "Scripts List"},
                        {"uri": "files://list", "name": "Files List"}
                    ]}
                }
                
                if method in method_mapping:
                    result = method_mapping[method]()
                    self._send_jsonrpc_response(request_id, result=result)
                else:
                    self._send_jsonrpc_response(request_id, error=f"Unknown method: {method}")
                    
            else:
                # Handle legacy HTTP API format
                tool_name = data.get('name')
                arguments = data.get('arguments', {})
                
                if tool_name:
                    result = self._call_tool(tool_name, arguments)
                    response = {"success": True, "result": result}
                else:
                    response = {"success": False, "error": "No tool name provided"}
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
        except Exception as e:
            self._send_jsonrpc_response(data.get("id", "unknown"), error=str(e))
    
    def _call_tool(self, tool_name, arguments):
        """Call a tool by name with arguments"""
        tool_mapping = {
            "list_scripts": lambda: list_scripts(),
            "get_script": lambda: get_script(**arguments),
            "load_script": lambda: load_script(**arguments),
            "get_script_progress": lambda: get_script_progress(),
            "advance_script_stage": lambda: advance_script_stage(),
            "reset_script": lambda: reset_script(),
            "clear_script": lambda: clear_script(),
            "read_file": lambda: read_file(**arguments),
            "write_file": lambda: write_file(**arguments),
            "append_file": lambda: append_file(**arguments),
            "list_files": lambda: list_files(),
            "get_file_info": lambda: get_file_info(**arguments),
            "create_file": lambda: create_file(**arguments),
            "create_backup": lambda: create_backup(**arguments),
        }
        
        if tool_name in tool_mapping:
            return tool_mapping[tool_name]()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

def run_server(port):
    server = HTTPServer(('0.0.0.0', port), MCPBridgeHandler)
    print(f"MCP JSON-RPC Bridge running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
