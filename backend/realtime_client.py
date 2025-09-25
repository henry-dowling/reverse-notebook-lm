import asyncio
import json
import websockets
from typing import Dict, Any, Callable, Optional
import logging
from config import OPENAI_API_KEY, REALTIME_CONFIG

logger = logging.getLogger(__name__)


class OpenAIRealtimeClient:
    """Client for connecting to OpenAI's Realtime API"""
    
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.session_id: Optional[str] = None
        self.tools: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self.is_connected = False
        self.url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    
    def register_tool(self, name: str, handler: Callable):
        """Register a tool function"""
        self.tools[name] = handler
        logger.info(f"Registered tool: {name}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_type] = handler
        logger.info(f"Registered event handler: {event_type}")
    
    async def connect(self):
        """Connect to OpenAI Realtime API"""
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            self.websocket = await websockets.connect(
                self.url,
                extra_headers=headers,
                ping_interval=None
            )
            
            self.is_connected = True
            logger.info("Connected to OpenAI Realtime API")
            
            # Send session update with configuration
            await self.send_session_update()
            
            # Start listening for events
            await self._listen_for_events()
            
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI Realtime API: {e}")
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from OpenAI Realtime API"""
        if self.websocket:
            await self.websocket.close()
        self.is_connected = False
        logger.info("Disconnected from OpenAI Realtime API")
    
    async def send_session_update(self):
        """Send session configuration to OpenAI"""
        session_config = {
            "type": "session.update",
            "session": REALTIME_CONFIG
        }
        await self._send_event(session_config)
        logger.info("Sent session configuration")
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to OpenAI"""
        if not self.is_connected:
            raise Exception("Not connected to OpenAI Realtime API")
        
        event = {
            "type": "input_audio_buffer.append",
            "audio": audio_data.hex()
        }
        await self._send_event(event)
    
    async def send_text(self, text: str):
        """Send text message to OpenAI"""
        if not self.is_connected:
            raise Exception("Not connected to OpenAI Realtime API")
        
        # Create conversation item
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        await self._send_event(event)
        
        # Trigger response generation
        response_event = {
            "type": "response.create"
        }
        await self._send_event(response_event)
    
    async def _send_event(self, event: Dict[str, Any]):
        """Send an event to OpenAI"""
        if not self.websocket:
            raise Exception("WebSocket not connected")
        
        event_json = json.dumps(event)
        await self.websocket.send(event_json)
        logger.debug(f"Sent event: {event.get('type')}")
    
    async def _listen_for_events(self):
        """Listen for events from OpenAI"""
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    await self._handle_event(event)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON: {e}")
                except Exception as e:
                    logger.error(f"Error handling event: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("OpenAI connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error in event listener: {e}")
            self.is_connected = False
    
    async def _handle_event(self, event: Dict[str, Any]):
        """Handle incoming events from OpenAI"""
        event_type = event.get("type")
        logger.debug(f"Received event: {event_type}")
        
        # Handle different event types
        if event_type == "session.created":
            self.session_id = event.get("session", {}).get("id")
            logger.info(f"Session created: {self.session_id}")
        
        elif event_type == "response.function_call_arguments.done":
            await self._handle_function_call(event)
        
        elif event_type == "response.audio.delta":
            audio_data = event.get("delta", "")
            if audio_data and "response.audio" in self.event_handlers:
                await self.event_handlers["response.audio"](audio_data)
        
        elif event_type == "response.audio.done":
            if "response.audio.done" in self.event_handlers:
                await self.event_handlers["response.audio.done"]()
        
        elif event_type == "response.text.delta":
            text_delta = event.get("delta", "")
            if text_delta and "response.text" in self.event_handlers:
                await self.event_handlers["response.text"](text_delta)
        
        elif event_type == "response.text.done":
            text = event.get("text", "")
            if "response.text.done" in self.event_handlers:
                await self.event_handlers["response.text.done"](text)
        
        elif event_type == "error":
            error = event.get("error", {})
            logger.error(f"OpenAI API error: {error}")
            if "error" in self.event_handlers:
                await self.event_handlers["error"](error)
        
        # Forward all events to registered handlers
        if event_type in self.event_handlers:
            await self.event_handlers[event_type](event)
    
    async def _handle_function_call(self, event: Dict[str, Any]):
        """Handle function call from OpenAI"""
        try:
            call_id = event.get("call_id")
            function_name = event.get("name")
            arguments = event.get("arguments", "{}")
            
            logger.info(f"Function call: {function_name} with call_id: {call_id}")
            
            # Parse arguments
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError:
                args = {}
            
            # Execute the function if registered
            if function_name in self.tools:
                try:
                    result = await self.tools[function_name](**args)
                    
                    # Send function call result back to OpenAI
                    response_event = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": json.dumps(result) if isinstance(result, dict) else str(result)
                        }
                    }
                    await self._send_event(response_event)
                    
                    # Trigger response generation
                    await self._send_event({"type": "response.create"})
                    
                except Exception as e:
                    logger.error(f"Error executing function {function_name}: {e}")
                    # Send error response
                    error_response = {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": json.dumps({
                                "error": str(e),
                                "success": False
                            })
                        }
                    }
                    await self._send_event(error_response)
                    await self._send_event({"type": "response.create"})
            else:
                logger.warning(f"Unknown function call: {function_name}")
                # Send error response for unknown function
                error_response = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps({
                            "error": f"Unknown function: {function_name}",
                            "success": False
                        })
                    }
                }
                await self._send_event(error_response)
                await self._send_event({"type": "response.create"})
                
        except Exception as e:
            logger.error(f"Error handling function call: {e}")
    
    async def commit_audio_buffer(self):
        """Commit the current audio buffer for processing"""
        if not self.is_connected:
            raise Exception("Not connected to OpenAI Realtime API")
        
        event = {
            "type": "input_audio_buffer.commit"
        }
        await self._send_event(event)
    
    async def cancel_response(self):
        """Cancel the current response generation"""
        if not self.is_connected:
            raise Exception("Not connected to OpenAI Realtime API")
        
        event = {
            "type": "response.cancel"
        }
        await self._send_event(event)