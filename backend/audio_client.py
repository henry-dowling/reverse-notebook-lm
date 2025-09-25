#!/usr/bin/env python3
"""
Direct audio client for AI Assistant - connects to computer audio like Hume implementation
"""

import asyncio
import pyaudio
import numpy as np
import logging
import threading
import queue
from pathlib import Path
import signal
import sys
from datetime import datetime

from realtime_client import OpenAIRealtimeClient
from handlers.file_handler import FileHandler
from handlers.script_library import ScriptLibrary
from tools.file_tool import FileOperationTool
from tools.script_tool import ScriptLoaderTool
from config import WORKING_DIRECTORY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioAssistant:
    """Direct audio client for AI Assistant"""
    
    def __init__(self):
        # Audio configuration
        self.SAMPLE_RATE = 16000
        self.CHUNK_SIZE = 1024
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16
        
        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        
        # Audio queues
        self.audio_queue = queue.Queue()
        self.playback_queue = queue.Queue()
        
        # Components
        self.file_handler = FileHandler(WORKING_DIRECTORY)
        self.script_library = ScriptLibrary()
        self.realtime_client = OpenAIRealtimeClient()
        
        # Tools
        self.file_tool = FileOperationTool(self.file_handler)
        self.script_tool = ScriptLoaderTool(self.script_library)
        
        # State
        self.running = False
        self.current_script = None
        
        self._setup_tools()
        self._setup_signal_handlers()
    
    def _setup_tools(self):
        """Register tools with OpenAI client"""
        self.realtime_client.register_tool("file_operation", self.file_tool.execute)
        self.realtime_client.register_tool("load_script", self.script_tool.execute)
        
        # Register audio event handlers
        self.realtime_client.register_event_handler("response.audio", self._handle_audio_response)
        self.realtime_client.register_event_handler("response.audio.done", self._handle_audio_done)
        self.realtime_client.register_event_handler("response.text.done", self._handle_text_response)
        
        logger.info("Tools and event handlers registered")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def list_audio_devices(self):
        """List available audio devices"""
        print("\n🎤 Available Audio Input Devices:")
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"  {i}: {device_info['name']} ({device_info['maxInputChannels']} channels)")
        
        print("\n🔊 Available Audio Output Devices:")
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                print(f"  {i}: {device_info['name']} ({device_info['maxOutputChannels']} channels)")
        print()
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input stream"""
        if status:
            logger.warning(f"Audio input status: {status}")
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Put audio data in queue for processing
        try:
            self.audio_queue.put_nowait(audio_data.tobytes())
        except queue.Full:
            logger.warning("Audio queue full, dropping frame")
        
        return (None, pyaudio.paContinue)
    
    def _playback_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio output stream"""
        if status:
            logger.warning(f"Audio output status: {status}")
        
        try:
            # Get audio data from playback queue
            audio_data = self.playback_queue.get_nowait()
            return (audio_data, pyaudio.paContinue)
        except queue.Empty:
            # Return silence if no audio to play
            silence = np.zeros(frame_count, dtype=np.int16).tobytes()
            return (silence, pyaudio.paContinue)
    
    async def start(self, input_device=None, output_device=None):
        """Start the audio assistant"""
        try:
            logger.info("Starting AI Audio Assistant...")
            
            # Create workspace
            workspace_path = Path(WORKING_DIRECTORY)
            workspace_path.mkdir(exist_ok=True)
            
            # Create default file if needed
            default_file = workspace_path / "output.md"
            if not default_file.exists():
                self.file_handler.create_file("output.md", f"# AI Assistant Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nReady to start!\n")
            
            # Connect to OpenAI
            logger.info("Connecting to OpenAI Realtime API...")
            await self.realtime_client.connect()
            
            # Start audio streams
            self._start_audio_streams(input_device, output_device)
            
            # Start audio processing
            self.running = True
            
            # Start background tasks
            audio_task = asyncio.create_task(self._process_audio())
            
            logger.info("🎤 AI Audio Assistant ready!")
            logger.info("💬 Start speaking - the AI is listening...")
            logger.info("📝 Available scripts: blog_writer, improv_game, email_workshop, brainstorm_session, interview_prep")
            logger.info("🗣️  Say 'load blog writer' or similar to start a script")
            logger.info("🛑 Press Ctrl+C to stop")
            
            # Keep running
            await self._keep_alive()
            
        except Exception as e:
            logger.error(f"Failed to start audio assistant: {e}")
            raise
    
    def _start_audio_streams(self, input_device=None, output_device=None):
        """Start audio input and output streams"""
        try:
            # Start input stream
            self.input_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                input_device_index=input_device,
                frames_per_buffer=self.CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            
            # Start output stream
            self.output_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                output=True,
                output_device_index=output_device,
                frames_per_buffer=self.CHUNK_SIZE,
                stream_callback=self._playback_callback
            )
            
            self.input_stream.start_stream()
            self.output_stream.start_stream()
            
            logger.info("Audio streams started")
            
        except Exception as e:
            logger.error(f"Failed to start audio streams: {e}")
            raise
    
    async def _process_audio(self):
        """Process audio data from the queue"""
        audio_buffer = b''
        last_send_time = asyncio.get_event_loop().time()
        
        while self.running:
            try:
                # Get audio data from queue
                try:
                    audio_data = self.audio_queue.get_nowait()
                    audio_buffer += audio_data
                except queue.Empty:
                    await asyncio.sleep(0.01)
                    continue
                
                # Send audio data to OpenAI in chunks
                current_time = asyncio.get_event_loop().time()
                if len(audio_buffer) >= self.CHUNK_SIZE * 2 or (current_time - last_send_time) > 0.1:
                    if audio_buffer:
                        # Send to OpenAI Realtime API
                        await self.realtime_client.send_audio(audio_buffer)
                        audio_buffer = b''
                        last_send_time = current_time
                
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                await asyncio.sleep(0.1)
    
    async def _handle_audio_response(self, audio_hex: str):
        """Handle audio response from OpenAI"""
        try:
            # Convert hex to bytes
            audio_bytes = bytes.fromhex(audio_hex)
            
            # Queue for playback
            try:
                self.playback_queue.put_nowait(audio_bytes)
            except queue.Full:
                logger.warning("Playback queue full, dropping audio")
                
        except Exception as e:
            logger.error(f"Error handling audio response: {e}")
    
    async def _handle_audio_done(self):
        """Handle audio response completion"""
        logger.info("🔊 AI finished speaking")
    
    async def _handle_text_response(self, text: str):
        """Handle text response from OpenAI"""
        print(f"\n🤖 AI: {text}\n")
        
        # Also save important responses to file
        timestamp = datetime.now().strftime("%H:%M:%S")
        content = f"\n**[{timestamp}] AI Response:**\n{text}\n"
        try:
            await self.file_tool.execute("append", "output.md", content)
        except Exception as e:
            logger.error(f"Error saving response to file: {e}")
    
    async def _keep_alive(self):
        """Keep the assistant running"""
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Keep-alive cancelled")
    
    def stop(self):
        """Stop the audio assistant"""
        logger.info("Stopping AI Audio Assistant...")
        self.running = False
        
        # Stop audio streams
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        # Terminate PyAudio
        self.audio.terminate()
        
        logger.info("Audio assistant stopped")


def main():
    """Main entry point"""
    assistant = AudioAssistant()
    
    # Show available devices
    assistant.list_audio_devices()
    
    # Ask user for device selection
    try:
        input_device = input("Select input device (press Enter for default): ").strip()
        input_device = int(input_device) if input_device else None
        
        output_device = input("Select output device (press Enter for default): ").strip()
        output_device = int(output_device) if output_device else None
        
    except (ValueError, KeyboardInterrupt):
        print("Using default devices...")
        input_device = None
        output_device = None
    
    # Start the assistant
    try:
        asyncio.run(assistant.start(input_device, output_device))
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        assistant.stop()


if __name__ == "__main__":
    main()