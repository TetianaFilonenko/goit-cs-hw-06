import http.server
import socketserver
import os
import json
import socket
from urllib.parse import parse_qs

PORT = 3000

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        elif self.path == '/message.html':
            self.path = 'message.html'
        elif self.path == '/style.css':
            self.path = 'style.css'
        elif self.path == '/logo.png':
            self.path = 'logo.png'
        else:
            self.path = 'error.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = parse_qs(post_data.decode('utf-8'))
            message_data = {
                "username": post_data['username'][0],
                "message": post_data['message'][0]
            }

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('socket', 5001))
            sock.sendall(json.dumps(message_data).encode('utf-8'))
            sock.close()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'Message sent'}).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Page not found')

os.chdir('static')
httpd = socketserver.TCPServer(("", PORT), Handler)
print(f"Serving on port {PORT}")
httpd.serve_forever()
