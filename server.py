from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

PORT = 7000  # Use your desired port
server_address = ('0.0.0.0', PORT)
httpd = HTTPServer(server_address, CORSRequestHandler)

print(f"Serving on http://0.0.0.0:{PORT}")
httpd.serve_forever()
