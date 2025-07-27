"""
Scientific Calculator System Launcher
=====================================

This script helps you start the calculator system components easily.
"""

import subprocess
import sys
import time
import threading
import webbrowser
import os
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("=" * 60)
    print("Scientific Calculator System")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if websockets is available"""
    try:
        import websockets
        print("websockets library found")
        return True
    except ImportError:
        print("Warning: 'websockets' package not found.")
        print("Install it with: pip install websockets")
        print("(Required for web interface)")
        print()
        return False

def start_server():
    """Start the calculator server"""
    print("Starting Calculator Server...")
    try:
        from server import CalculatorServer
        server = CalculatorServer()
        server.start()
    except KeyboardInterrupt:
        print("\n Calculator server stopped")
    except Exception as e:
        print(f"Error starting server: {e}")

def start_bridge():
    """Start the WebSocket bridge"""
    print("Starting WebSocket Bridge...")
    try:
        from simple_bridge import SimpleWebSocketBridge
        bridge = SimpleWebSocketBridge()
        bridge.run()
    except ImportError:
        print("Error: simple_bridge.py not found")
        print("Make sure simple_bridge.py is in the current directory")
    except KeyboardInterrupt:
        print("\n WebSocket bridge stopped")
    except Exception as e:
        print(f"Error starting bridge: {e}")

def start_cli_client():
    """Start the CLI client"""
    print("Starting CLI Client...")
    try:
        from client import CalculatorCLI
        cli = CalculatorCLI()
        cli.start()
    except KeyboardInterrupt:
        print("\n CLI client stopped")
    except Exception as e:
        print(f"Error starting CLI: {e}")

def open_web_interface():
    """Open the web interface in browser"""
    html_file = Path("calculator.html")
    if html_file.exists():
        print("Opening web interface...")
        webbrowser.open(f"file://{html_file.absolute()}")
    else:
        print("calculator.html not found in current directory")

def show_menu():
    """Show the main menu"""
    print("Choose how to run the calculator:")
    print()
    print("1. Web Interface (Full System)")
    print("   - Starts server + WebSocket bridge")
    print("   - Opens calculator in browser")
    print()
    print("2. CLI Interface")
    print("   - Starts server + command-line client")
    print()
    print("3. Server Only")
    print("   - Just starts the calculation server")
    print()
    print("4. Bridge Only")
    print("   - Just starts the WebSocket bridge")
    print("   - (Requires server to be running)")
    print()
    print("5. Help & Information")
    print()
    print("0. Exit")
    print()

def show_help():
    """Show help information"""
    print("Calculator System Help")
    print("=" * 40)
    print()
    print("System Architecture:")
    print("   • server.py: Python socket server for calculations")
    print("   • websocket_bridge.py: Bridges web browsers to socket server")
    print("   • calculator.html: Modern web interface")
    print("   • client.py: Command-line interface")
    print()
    print("Manual Startup (Advanced):")
    print("   1. python server.py")
    print("   2. python websocket_bridge.py")
    print("   3. Open calculator.html in browser")
    print()
    print("Requirements:")
    print("   • Python 3.7+")
    print("   • websockets package (pip install websockets)")
    print()
    print("Default Ports:")
    print("   • Calculator Server: localhost:8888")
    print("   • WebSocket Bridge: localhost:8080")
    print()

def main():
    """Main launcher function"""
    print_banner()
    
    has_websockets = check_dependencies()
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-5): ").strip()
        except KeyboardInterrupt:
            print("\n Goodbye!")
            sys.exit(0)
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            if not has_websockets:
                print("WebSocket bridge requires 'websockets' package")
                continue
            
            print("Starting Full Web System...")
            print("   This will start both server and bridge, then open browser")
            print("   Press Ctrl+C to stop all components")
            print()
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            print("Waiting for server to start...")
            time.sleep(2)
            
            bridge_thread = threading.Thread(target=start_bridge, daemon=True)
            bridge_thread.start()
            
            print("Waiting for bridge to start...")
            time.sleep(2)
            
            open_web_interface()
            
            try:
                print("System running! Press Ctrl+C to stop.")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n Stopping system...")
                break
                
        elif choice == "2":
            print("Starting CLI System...")
            print("   This will start server and CLI client")
            print("   Press Ctrl+C to stop")
            print()
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            print("Waiting for server to start...")
            time.sleep(2)
            
            start_cli_client()
            
        elif choice == "3":
            print("Starting Server Only...")
            start_server()
            
        elif choice == "4":
            if not has_websockets:
                print("WebSocket bridge requires 'websockets' package")
                continue
            print("Starting Bridge Only...")
            print("   Make sure the calculator server is running!")
            start_bridge()
            
        elif choice == "5":
            show_help()
            input("\nPress Enter to continue...")
            
        else:
            print("Invalid choice. Please try again.")
        
        print()

if __name__ == "__main__":
    main()