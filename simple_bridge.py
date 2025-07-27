"""
Simple WebSocket to Socket Bridge
Compatible with various websockets library versions
"""

import asyncio
import socket
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
    logger.info("websockets library found")
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.error("websockets library not found. Install with: pip install websockets")

class SimpleWebSocketBridge:
    """Simple WebSocket to Socket Bridge"""
    
    def __init__(self, websocket_host='localhost', websocket_port=8080, socket_host='localhost', socket_port=8888):
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.clients = set()
        
    async def handle_client(self, websocket, path=None):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        
        try:
            client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            logger.info(f"Client connected: {client_address}")
            
            welcome = {"success": True, "message": "Connected to calculator", "type": "connection"}
            await websocket.send(json.dumps(welcome))
            
            async for message in websocket:
                try:
                    logger.info(f"Received: {message}")
                    request = json.loads(message)
                    
                    response = await self.forward_to_socket_server(request)
                    
                    logger.info(f"Sending: {response}")
                    await websocket.send(json.dumps(response))
                    
                except json.JSONDecodeError as e:
                    error_msg = {"success": False, "error": f"Invalid JSON: {str(e)}"}
                    await websocket.send(json.dumps(error_msg))
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    error_msg = {"success": False, "error": f"Processing error: {str(e)}"}
                    await websocket.send(json.dumps(error_msg))
                    
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            self.clients.discard(websocket)
            logger.info("Client disconnected")
    
    async def forward_to_socket_server(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to socket server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.socket_host, self.socket_port))
            
            request_json = json.dumps(request)
            sock.send(request_json.encode('utf-8'))
            
            response_data = sock.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            
            sock.close()
            return response
            
        except ConnectionRefusedError:
            return {"success": False, "error": "Calculator server not running. Start server.py first."}
        except socket.timeout:
            return {"success": False, "error": "Calculator server timeout"}
        except Exception as e:
            logger.error(f"Socket error: {e}")
            return {"success": False, "error": f"Communication error: {str(e)}"}
    
    def test_socket_server(self):
        """Test connection to socket server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.socket_host, self.socket_port))
            
            test_msg = {"command": "ping"}
            sock.send(json.dumps(test_msg).encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            sock.close()
            
            logger.info("✓ Calculator server is reachable")
            return True
        except Exception as e:
            logger.warning(f"⚠ Calculator server not reachable: {e}")
            logger.warning("Make sure to run 'python server.py' first")
            return False
    
    async def start_server(self):
        """Start the WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            logger.error("Cannot start server: websockets library not available")
            return
        
        logger.info(f"Starting WebSocket bridge on {self.websocket_host}:{self.websocket_port}")
        logger.info(f"Will connect to calculator server at {self.socket_host}:{self.socket_port}")
        
        self.test_socket_server()
        
        try:
            server = await websockets.serve(
                self.handle_client,
                self.websocket_host,
                self.websocket_port
            )
            
            logger.info(f"✓ WebSocket bridge running on ws://{self.websocket_host}:{self.websocket_port}")
            logger.info("Open calculator.html in your browser")
            logger.info("Press Ctrl+C to stop")
            
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
    
    def run(self):
        """Run the bridge"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            logger.info("Bridge stopped by user")
        except Exception as e:
            logger.error(f"Bridge error: {e}")

def main():
    """Main entry point"""
    if not WEBSOCKETS_AVAILABLE:
        print("Error: websockets library not found")
        print("Install it with: pip install websockets")
        return
    
    bridge = SimpleWebSocketBridge()
    bridge.run()

if __name__ == "__main__":
    main()