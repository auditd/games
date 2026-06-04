#!/usr/bin/env python3
import socket
import sys
import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable caching or add headers if necessary
        super().end_headers()

def find_free_port(start_port=8000):
    port = start_port
    while port < 9000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # If connect_ex returns 0, the port is active (in use)
            # If it returns non-zero, we might be able to use it.
            if s.connect_ex(('127.0.0.1', port)) != 0:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except socket.error:
                    pass
        port += 1
    return start_port

def open_browser(url):
    time.sleep(1.2)
    print(f"Opening browser at {url}...")
    webbrowser.open(url)

def main():
    host = '127.0.0.1'
    start_port = 8000
    port = find_free_port(start_port)
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    
    url = f"http://{host}:{port}/"
    print(f"==================================================")
    print(f"  Galaga Retro Arcade Local Server Starting")
    print(f"  Serving files from the current directory.")
    print(f"  URL: {url}")
    if port != start_port:
        print(f"  [Notice] Port {start_port} was in use. Automatically switched to {port}.")
    print(f"  Press Ctrl+C to stop the server.")
    print(f"==================================================")
    
    # Run browser auto-opening in a background thread to prevent blocking
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
        sys.exit(0)

if __name__ == '__main__':
    main()
