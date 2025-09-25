#!/usr/bin/env python3
"""
Start the Pure MCP Server with ngrok for remote access
This script runs the actual MCP protocol server (not HTTP wrapper) with ngrok tunneling
"""

import subprocess
import time
import sys
import json
import requests
import signal
import os
from pathlib import Path

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ngrok():
    """Install ngrok if not present"""
    print("ngrok not found. Please install it:")
    print("1. Go to https://ngrok.com/download")
    print("2. Download and install ngrok")
    print("3. Sign up for a free account and get your auth token")
    print("4. Run: ngrok config add-authtoken YOUR_TOKEN")
    return False

def start_ngrok(port=8000, config_file=None):
    """Start ngrok tunnel using configuration file"""
    print(f"Starting ngrok tunnel on port {port}...")
    
    # Use ngrok config file if available
    if config_file and Path(config_file).exists():
        print(f"Using ngrok config file: {config_file}")
        ngrok_cmd = ["ngrok", "start", "app1", "--config", str(config_file), "--log=stdout"]
    else:
        # Fallback to command line arguments
        ngrok_cmd = ["ngrok", "http", str(port), "--log=stdout"]
        print("Using command line arguments (no config file)")
    
    # Start ngrok in background
    ngrok_process = subprocess.Popen(
        ngrok_cmd,
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    # Wait a moment for ngrok to start
    time.sleep(3)
    
    # Check if ngrok process is still running
    if ngrok_process.poll() is not None:
        stdout, stderr = ngrok_process.communicate()
        print(f"❌ ngrok failed to start")
        if stderr:
            print(f"Error: {stderr.decode()}")
        return ngrok_process, None
    
    # Get the public URL
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
            tunnels = response.json()
            
            if tunnels["tunnels"]:
                public_url = tunnels["tunnels"][0]["public_url"]
                print(f"✅ ngrok tunnel started: {public_url}")
                return ngrok_process, public_url
            else:
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting for ngrok tunnel... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                    continue
                else:
                    print("❌ Failed to get ngrok tunnel URL after multiple attempts")
                    return ngrok_process, None
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"⏳ Waiting for ngrok API... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
            else:
                print(f"❌ Error getting ngrok URL: {e}")
                return ngrok_process, None
        except Exception as e:
            print(f"❌ Unexpected error getting ngrok URL: {e}")
            return ngrok_process, None
    
    return ngrok_process, None

def start_mcp_server():
    """Start the Pure MCP server"""
    print(f"Starting Pure MCP Server...")
    
    server_process = subprocess.Popen([
        sys.executable, "mcp_server.py"
    ])
    
    # Wait a moment for server to start
    time.sleep(2)
    
    return server_process

def load_ngrok_config():
    """Load ngrok configuration file"""
    # Look for ngrok.yml config file
    config_file = Path(__file__).parent / "ngrok.yml"
    
    if config_file.exists():
        print(f"✅ Found ngrok config file: {config_file}")
        return str(config_file)
    else:
        print("⚠️  No ngrok.yml config file found, using command line arguments")
        return None

def create_mcp_http_bridge(port=8000):
    """Create a simple HTTP bridge for the MCP server to make it accessible via HTTP"""
    print(f"Creating HTTP bridge for MCP server on port {port}...")
    
    # Create a proper MCP-to-HTTP bridge that handles JSON-RPC protocol
    bridge_code = '''
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
'''
    
    bridge_file = Path(__file__).parent / "mcp_bridge.py"
    with open(bridge_file, 'w') as f:
        f.write(bridge_code)
    
    bridge_process = subprocess.Popen([
        sys.executable, "mcp_bridge.py", str(port)
    ])
    
    return bridge_process

def main():
    """Main function"""
    port = 8000
    
    print("🚀 Starting Pure MCP Server with ngrok")
    print("=" * 50)
    
    # Load ngrok configuration
    config_file = load_ngrok_config()
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        if not install_ngrok():
            return
    
    # Start the Pure MCP server
    mcp_process = start_mcp_server()
    
    # Create HTTP bridge for the MCP server
    bridge_process = create_mcp_http_bridge(port)
    
    # Start ngrok with configuration
    ngrok_process, public_url = start_ngrok(port, config_file)
    
    if not public_url:
        print("❌ Failed to start ngrok tunnel")
        mcp_process.terminate()
        bridge_process.terminate()
        return
    
    print("\n" + "=" * 50)
    print("🎉 Pure MCP Server is running!")
    print(f"📡 Public URL: {public_url}")
    print(f"🏠 Local URL: http://localhost:{port}")
    print("\n📋 Available endpoints:")
    print(f"  - {public_url}/health - Health check")
    print(f"  - {public_url}/scripts - List scripts")
    print(f"  - {public_url}/files - List files")
    print(f"  - POST {public_url}/ - Call MCP tools")
    print("\n🔧 MCP Protocol:")
    print(f"  - Pure MCP server running in background")
    print(f"  - JSON-RPC bridge available for MCP Inspector")
    print(f"  - Compatible with MCP protocol specifications")
    print("\n⏹️  Press Ctrl+C to stop all services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if mcp_process.poll() is not None:
                print("❌ MCP server stopped unexpectedly")
                break
                
            if bridge_process.poll() is not None:
                print("❌ HTTP bridge stopped unexpectedly")
                break
                
            if ngrok_process.poll() is not None:
                print("❌ ngrok stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    finally:
        # Clean up processes
        if mcp_process.poll() is None:
            mcp_process.terminate()
            mcp_process.wait()
        
        if bridge_process.poll() is None:
            bridge_process.terminate()
            bridge_process.wait()
        
        if ngrok_process.poll() is None:
            ngrok_process.terminate()
            ngrok_process.wait()
        
        # Clean up bridge file
        bridge_file = Path(__file__).parent / "mcp_bridge.py"
        if bridge_file.exists():
            bridge_file.unlink()
        
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
