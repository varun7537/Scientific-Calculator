import asyncio
import websockets
import socket
import json
import threading
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebSocketToSocketBridge:
    """Bridge between WebSocket clients and Python socket server"""
    
    def __init__(self, websocket_host='localhost', websocket_port=8080, socket_host='localhost', socket_port=8888):
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.clients = set()
        
    async def handle_websocket_client(self, websocket, path=None):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        client_address = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logging.info(f"WebSocket client connected from {client_address}")
        
        try:
            welcome_msg = {"success": True, "message": "Connected to calculator server", "type": "connection"}
            await websocket.send(json.dumps(welcome_msg))
            
            async for message in websocket:
                try:
                    logging.info(f"Received from {client_address}: {message}")
                    
                    request = json.loads(message)
                    
                    response = await self.forward_to_socket_server(request)
                    
                    logging.info(f"Sending to {client_address}: {response}")
                    
                    await websocket.send(json.dumps(response))
                    
                except json.JSONDecodeError as e:
                    error_response = {"success": False, "error": f"Invalid JSON format: {str(e)}"}
                    await websocket.send(json.dumps(error_response))
                except Exception as e:
                    logging.error(f"Error processing message from {client_address}: {e}")
                    error_response = {"success": False, "error": f"Bridge error: {str(e)}"}
                    await websocket.send(json.dumps(error_response))
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"WebSocket client {client_address} disconnected normally")
        except websockets.exceptions.ConnectionClosedError:
            logging.info(f"WebSocket client {client_address} disconnected unexpectedly")
        except Exception as e:
            logging.error(f"Error handling WebSocket client {client_address}: {e}")
        finally:
            self.clients.discard(websocket)
            logging.info(f"Cleaned up connection with {client_address}")
    
    async def forward_to_socket_server(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Forward request to Python socket server and return response"""
        try:
            logging.info(f"Forwarding to socket server: {request}")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            sock.connect((self.socket_host, self.socket_port))
            
            request_json = json.dumps(request)
            sock.send(request_json.encode('utf-8'))
            
            response_data = sock.recv(4096).decode('utf-8') 
            response = json.loads(response_data)
            
            sock.close()
            
            logging.info(f"Received from socket server: {response}")
            return response
            
        except socket.timeout:
            logging.error("Socket server timeout")
            return {"success": False, "error": "Calculator server timeout"}
        except ConnectionRefusedError:
            logging.error("Socket server connection refused")
            return {"success": False, "error": "Calculator server not available. Make sure server.py is running."}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON from socket server: {e}")
            return {"success": False, "error": "Invalid response from calculator server"}
        except Exception as e:
            logging.error(f"Socket communication error: {e}")
            return {"success": False, "error": f"Communication error: {str(e)}"}
    
    async def start_websocket_server(self):
        """Start the WebSocket server"""
        logging.info(f"Starting WebSocket bridge on {self.websocket_host}:{self.websocket_port}")
        logging.info(f"Connecting to calculator server at {self.socket_host}:{self.socket_port}")
        
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(5)
            test_sock.connect((self.socket_host, self.socket_port))
            
            test_request = {"command": "ping"}
            test_sock.send(json.dumps(test_request).encode('utf-8'))
            test_response = test_sock.recv(1024).decode('utf-8')
            test_sock.close()
            
            logging.info("✓ Calculator server is reachable and responding")
        except Exception as e:
            logging.warning(f"⚠ Warning: Cannot reach calculator server: {e}")
            logging.warning("Make sure to run 'python server.py' before connecting clients")
        
        server = await websockets.serve(
            self.handle_websocket_client,
            self.websocket_host,
            self.websocket_port
        )
        
        logging.info(f"✓ WebSocket bridge running on ws://{self.websocket_host}:{self.websocket_port}")
        logging.info("Open the calculator.html file in your browser to use the calculator")
        logging.info("Press Ctrl+C to stop the server")
        
        await server.wait_closed()
    
    def run(self):
        """Run the WebSocket bridge"""
        try:
            asyncio.run(self.start_websocket_server())
        except KeyboardInterrupt:
            print("\nWebSocket bridge stopped by user")
        except Exception as e:
            print(f"Error running WebSocket bridge: {e}")

if __name__ == "__main__":
    bridge = WebSocketToSocketBridge()
    bridge.run()