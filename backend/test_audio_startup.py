#!/usr/bin/env python3
"""
Test script to verify audio client startup without interactive input
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from debug_audio_client import DebugAudioAssistant

async def test_startup():
    """Test the audio client startup process"""
    print("🧪 Testing audio client startup...")
    
    try:
        # Create assistant
        assistant = DebugAudioAssistant()
        print("✅ AudioAssistant created successfully")
        
        # Use default devices (no user input)
        input_device = 1  # MacBook Pro Microphone
        output_device = 2  # MacBook Pro Speakers
        
        print(f"🎤 Using input device: {input_device}")
        print(f"🔊 Using output device: {output_device}")
        
        # Start the assistant (this will show us exactly where it gets stuck)
        print("\n🚀 Starting audio assistant...")
        await assistant.start(input_device, output_device)
        
        return True
        
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_startup())
    if success:
        print("\n🎉 Audio client startup test completed!")
    else:
        print("\n🔧 Startup test failed - check the error messages above")
    sys.exit(0 if success else 1)
