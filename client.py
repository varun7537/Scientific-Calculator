import socket
import json
import threading
from typing import Dict, Any, Callable

class CalculatorClient:
    """Client for connecting to the scientific calculator server"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to the calculator server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to calculator server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        self.connected = False
        print("Disconnected from server")
    
    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to server and get response"""
        if not self.connected:
            return {"success": False, "error": "Not connected to server"}
        
        try:
            request_json = json.dumps(request)
            self.socket.send(request_json.encode('utf-8'))
            
            response_data = self.socket.recv(1024).decode('utf-8')
            response = json.loads(response_data)
            return response
            
        except Exception as e:
            return {"success": False, "error": f"Communication error: {str(e)}"}
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Send calculation request to server"""
        request = {
            "command": "calculate",
            "expression": expression
        }
        return self.send_request(request)
    
    def memory_operation(self, operation: str, value: float = None) -> Dict[str, Any]:
        """Send memory operation request to server"""
        request = {
            "command": "memory",
            "operation": operation
        }
        if value is not None:
            request["value"] = value
        return self.send_request(request)
    
    def ping(self) -> Dict[str, Any]:
        """Ping the server to check connection"""
        request = {"command": "ping"}
        return self.send_request(request)

class CalculatorCLI:
    """Command-line interface for the calculator client"""
    
    def __init__(self):
        self.client = CalculatorClient()
        self.running = False
        
    def print_help(self):
        """Print help information"""
        help_text = """
Scientific Calculator Commands:
=============================
Mathematical Operations:
    Basic: +, -, *, /, ** (power), % (modulo)
    Functions: sin(x), cos(x), tan(x), asin(x), acos(x), atan(x)
                sinh(x), cosh(x), tanh(x), log(x), ln(x), sqrt(x)
                exp(x), abs(x), floor(x), ceil(x), factorial(x)
    Constants: pi, e

Memory Operations:
    :ms [value]  - Store value in memory (or last result if no value)
    :mr          - Recall memory value
    :mc          - Clear memory
    :ma [value]  - Add value to memory (or last result if no value)

System Commands:
    :help        - Show this help
    :ping        - Test server connection
    :quit        - Exit calculator

Examples:
    2 + 3 * 4
    sin(pi/2)
    sqrt(16) + log(100)
    factorial(5)
    2**8
        """
        print(help_text)
    
    def start(self):
        """Start the CLI calculator"""
        print("Scientific Calculator Client")
        print("============================")
        
        if not self.client.connect():
            print("Failed to connect to calculator server. Make sure the server is running.")
            return
        
        ping_result = self.client.ping()
        if not ping_result.get("success"):
            print("Server connection test failed")
            return
        
        print("Type ':help' for commands or ':quit' to exit")
        print("Enter mathematical expressions to calculate")
        print()
        
        self.running = True
        
        while self.running:
            try:
                user_input = input("calc> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith(':'):
                    self.handle_command(user_input)
                else:
                    self.handle_calculation(user_input)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                print("\nExiting...")
                break
        
        self.client.disconnect()
    
    def handle_command(self, command: str):
        """Handle system commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == ':help':
            self.print_help()
        elif cmd == ':quit':
            self.running = False
        elif cmd == ':ping':
            result = self.client.ping()
            if result.get("success"):
                print("Server is responsive")
            else:
                print(f"Ping failed: {result.get('error', 'Unknown error')}")
        elif cmd == ':ms':  
            value = None
            if len(parts) > 1:
                try:
                    value = float(parts[1])
                except ValueError:
                    print("Invalid value for memory store")
                    return
            result = self.client.memory_operation("store", value)
            self.handle_memory_result(result)
        elif cmd == ':mr':  
            result = self.client.memory_operation("recall")
            self.handle_memory_result(result)
        elif cmd == ':mc':  
            result = self.client.memory_operation("clear")
            self.handle_memory_result(result)
        elif cmd == ':ma':  
            value = None
            if len(parts) > 1:
                try:
                    value = float(parts[1])
                except ValueError:
                    print("Invalid value for memory add")
                    return
            result = self.client.memory_operation("add", value)
            self.handle_memory_result(result)
        else:
            print(f"Unknown command: {cmd}")
            print("Type ':help' for available commands")
    
    def handle_calculation(self, expression: str):
        """Handle mathematical calculations"""
        result = self.client.calculate(expression)
        
        if result.get("success"):
            formatted_result = result.get("formatted_result", result.get("result"))
            print(f"= {formatted_result}")
        else:
            error = result.get("error", "Unknown error")
            print(f"Error: {error}")
    
    def handle_memory_result(self, result: Dict[str, Any]):
        """Handle memory operation results"""
        if result.get("success"):
            memory_value = result.get("memory", 0)
            operation = result.get("operation", "")
            print(f"Memory {operation}: {memory_value}")
        else:
            error = result.get("error", "Unknown error")
            print(f"Memory error: {error}")

if __name__ == "__main__":
    cli = CalculatorCLI()
    cli.start()