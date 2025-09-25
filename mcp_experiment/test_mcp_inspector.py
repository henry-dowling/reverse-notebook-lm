#!/usr/bin/env python3
"""
Test script to demonstrate proper MCP Inspector usage
"""

import subprocess
import sys
import time

def main():
    print("🔍 MCP Inspector Test Guide")
    print("=" * 50)
    print()
    print("The MCP Inspector should be used with the PURE MCP server, not HTTP.")
    print()
    print("✅ CORRECT WAY:")
    print("   cd backend")
    print("   npx @modelcontextprotocol/inspector node mcp_server.py")
    print()
    print("❌ WRONG WAY (causes proxy auth errors):")
    print("   npx @modelcontextprotocol/inspector http http://localhost:8000")
    print()
    print("📋 Available scripts:")
    print("   1. start_with_ngrok.py     - HTTP API server with ngrok")
    print("   2. start_mcp_with_ngrok.py - Pure MCP server with HTTP bridge")
    print("   3. mcp_server.py           - Pure MCP server only")
    print()
    print("🎯 For MCP Inspector testing:")
    print("   Use option 3 (mcp_server.py) with the inspector command above")
    print()
    print("🌐 For web/HTTP clients (ElevenLabs, etc.):")
    print("   Use option 1 (start_with_ngrok.py)")
    print()
    
    # Ask if user wants to run the inspector
    response = input("Would you like to run the MCP Inspector now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("\n🚀 Starting MCP Inspector...")
        print("This will open in your browser at http://localhost:6274")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            subprocess.run([
                "npx", "@modelcontextprotocol/inspector", 
                "node", "mcp_server.py"
            ])
        except KeyboardInterrupt:
            print("\n✅ MCP Inspector stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("✅ Use the command above when you're ready to test!")

if __name__ == "__main__":
    main()
