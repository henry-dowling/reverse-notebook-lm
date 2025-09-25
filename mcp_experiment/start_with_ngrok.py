#!/usr/bin/env python3
"""
Start the HTTP MCP Server with ngrok for remote access
"""

import subprocess
import time
import sys
import json
import requests
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

def start_server(port=8000):
    """Start the HTTP MCP server"""
    print(f"Starting HTTP MCP Server on port {port}...")
    
    server_process = subprocess.Popen([
        sys.executable, "http_mcp_server.py",
        "--host", "0.0.0.0",
        "--port", str(port)
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

def main():
    """Main function"""
    port = 8000
    
    print("🚀 Starting Reverse Notebook LM with ngrok")
    print("=" * 50)
    
    # Load ngrok configuration
    config_file = load_ngrok_config()
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        if not install_ngrok():
            return
    
    # Start the HTTP server
    server_process = start_server(port)
    
    # Start ngrok with configuration
    ngrok_process, public_url = start_ngrok(port, config_file)
    
    if not public_url:
        print("❌ Failed to start ngrok tunnel")
        server_process.terminate()
        return
    
    print("\n" + "=" * 50)
    print("🎉 Server is running!")
    print(f"📡 Public URL: {public_url}")
    print(f"🏠 Local URL: http://localhost:{port}")
    print("\n📋 Available endpoints:")
    print(f"  - {public_url}/tools - List MCP tools")
    print(f"  - {public_url}/scripts - List scripts")
    print(f"  - {public_url}/files - List files")
    print("\n⏹️  Press Ctrl+C to stop both server and ngrok")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                print("❌ HTTP server stopped unexpectedly")
                break
                
            if ngrok_process.poll() is not None:
                print("❌ ngrok stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    
    finally:
        # Clean up processes
        if server_process.poll() is None:
            server_process.terminate()
            server_process.wait()
        
        if ngrok_process.poll() is None:
            ngrok_process.terminate()
            ngrok_process.wait()
        
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()
