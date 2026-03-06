#!/usr/bin/env python3
"""
Simple HTTP Server for Frontend Development
Serves files from the frontend directory with CORS support

Usage:
    python server.py
    
Then open browser at: http://localhost:8000
"""

import http.server
import socketserver
import os
from pathlib import Path

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        """Add CORS headers to response"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        """Handle GET requests"""
        # Serve index.html for root path
        if self.path == '/' or self.path == '/index.html':
            self.path = '/index.html'
        return super().do_GET()

def main():
    """Start HTTP server"""
    PORT = 8000
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent.absolute()
    os.chdir(frontend_dir)
    
    handler = CORSRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"✅ Server started")
    print(f"📍 Open in browser: http://localhost:{PORT}")
    print(f"📁 Serving from: {frontend_dir}")
    print(f"🛑 Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    main()
