#!/usr/bin/env python3
"""
Simple microphone test to check permissions and audio access
"""

import pyaudio
import numpy as np
import time

def test_microphone():
    """Test microphone access and permissions"""
    print("🎤 Testing microphone access...")
    
    try:
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        print("✅ PyAudio initialized successfully")
        
        # List audio devices
        print("\n📱 Available audio devices:")
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"  {i}: {device_info['name']} ({device_info['maxInputChannels']} channels)")
        
        # Try to open an audio stream
        print("\n🔊 Testing audio stream...")
        
        # Audio configuration
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        # Open input stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("✅ Audio stream opened successfully!")
        print("🎤 Microphone access granted!")
        
        # Record a small sample
        print("📹 Recording 2 seconds of audio...")
        frames = []
        for i in range(int(RATE / CHUNK * 2)):  # 2 seconds
            data = stream.read(CHUNK)
            frames.append(data)
        
        # Convert to numpy array to check for actual audio
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        audio_level = np.sqrt(np.mean(audio_data**2))
        
        print(f"📊 Audio level detected: {audio_level:.2f}")
        
        if audio_level > 100:
            print("✅ Audio input detected - microphone is working!")
        else:
            print("⚠️  Very low audio level - check microphone or speak louder")
        
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        return True
        
    except OSError as e:
        if "Permission denied" in str(e) or "Input/output error" in str(e):
            print("❌ Microphone permission denied!")
            print("\n🔧 To fix this on macOS:")
            print("1. Go to System Preferences > Security & Privacy > Privacy > Microphone")
            print("2. Find 'Python' or 'Terminal' in the list")
            print("3. Check the box to allow microphone access")
            print("4. Restart the application")
            return False
        else:
            print(f"❌ Audio error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_microphone()
    if not success:
        print("\n💡 Try running this script again after granting permissions")
        print("   The system should prompt you for microphone access")
