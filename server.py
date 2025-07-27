import socket
import json
import math
import threading
from typing import Dict, Any

class ScientificCalculator:
    """Scientific calculator with comprehensive mathematical operations"""
    
    def __init__(self):
        self.memory = 0
        self.last_result = 0
        
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate mathematical expression and return result
        """
        try:
            safe_dict = {
                "__builtins__": {},
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "asin": math.asin,
                "acos": math.acos,
                "atan": math.atan,
                "sinh": math.sinh,
                "cosh": math.cosh,
                "tanh": math.tanh,
                "log": math.log10,
                "ln": math.log,
                "log10": math.log10,
                "log2": math.log2,
                "sqrt": math.sqrt,
                "exp": math.exp,
                "pow": pow,
                "abs": abs,
                "floor": math.floor,
                "ceil": math.ceil,
                "round": round,
                "pi": math.pi,
                "e": math.e,
                "factorial": math.factorial,
                "degrees": math.degrees,
                "radians": math.radians,
                "gcd": math.gcd,
                "lcm": math.lcm if hasattr(math, 'lcm') else lambda a, b: abs(a * b) // math.gcd(a, b)
            }
            
            expression = expression.replace('^', '**') 
            expression = expression.replace('π', str(math.pi))
            expression = expression.replace('e', str(math.e))
            
            result = eval(expression, safe_dict)
            self.last_result = result
            
            return {
                "success": True,
                "result": result,
                "expression": expression,
                "formatted_result": self._format_result(result)
            }
            
        except ZeroDivisionError:
            return {"success": False, "error": "Division by zero"}
        except ValueError as e:
            return {"success": False, "error": f"Math error: {str(e)}"}
        except SyntaxError:
            return {"success": False, "error": "Invalid expression"}
        except Exception as e:
            return {"success": False, "error": f"Error: {str(e)}"}
    
    def _format_result(self, result) -> str:
        """Format result for display"""
        if isinstance(result, float):
            if result.is_integer():
                return str(int(result))
            elif abs(result) > 1e10 or (abs(result) < 1e-6 and result != 0):
                return f"{result:.6e}"
            else:
                return f"{result:.10f}".rstrip('0').rstrip('.')
        return str(result)
    
    def memory_operation(self, operation: str, value: float = None) -> Dict[str, Any]:
        """Handle memory operations"""
        try:
            if operation == "store":
                self.memory = value if value is not None else self.last_result
                return {"success": True, "memory": self.memory, "operation": "stored"}
            elif operation == "recall":
                return {"success": True, "memory": self.memory, "operation": "recalled"}
            elif operation == "clear":
                self.memory = 0
                return {"success": True, "memory": self.memory, "operation": "cleared"}
            elif operation == "add":
                self.memory += value if value is not None else self.last_result
                return {"success": True, "memory": self.memory, "operation": "added"}
            else:
                return {"success": False, "error": "Invalid memory operation"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class CalculatorServer:
    """Socket server for scientific calculator"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.calculator = ScientificCalculator()
        self.running = False
        
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        print(f"Connection from {address}")
        
        try:
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    request = json.loads(data)
                    command = request.get('command')
                    
                    if command == 'calculate':
                        expression = request.get('expression', '')
                        response = self.calculator.calculate(expression)
                    elif command == 'memory':
                        operation = request.get('operation')
                        value = request.get('value')
                        response = self.calculator.memory_operation(operation, value)
                    elif command == 'ping':
                        response = {"success": True, "message": "Server is running"}
                    else:
                        response = {"success": False, "error": "Unknown command"}
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    error_response = {"success": False, "error": "Invalid JSON format"}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                except Exception as e:
                    error_response = {"success": False, "error": f"Server error: {str(e)}"}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))
                    
        except ConnectionResetError:
            print(f"Client {address} disconnected")
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"Connection with {address} closed")
    
    def start(self):
        """Start the calculator server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.running = True
            print(f"Scientific Calculator Server started on {self.host}:{self.port}")
            print("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except KeyboardInterrupt:
                    print("\nShutting down server...")
                    break
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"Failed to start server: {e}")
        finally:
            self.running = False
            try:
                server_socket.close()
            except:
                pass
            print("Server stopped")
    
    def stop(self):
        """Stop the server"""
        self.running = False

if __name__ == "__main__":
    server = CalculatorServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        server.stop()