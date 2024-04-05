from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import threading
import urllib.parse
import json
from datetime import datetime

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/style.css':
            self.send_static_file('style.css', 'text/css')
        elif pr_url.path == '/logo.png':
            self.send_static_file('logo.png', 'image/png')
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static_file(self, filename, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        data_dict['timestamp'] = str(datetime.now())
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.sendto(json.dumps(data_dict).encode(), ('localhost', 5000))
        self.send_response(302)
        self.send_header('Location', '/message')
        self.end_headers()

def run_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, HttpHandler)
    print('HTTP server started on port 3000\nhttp://localhost:3000/')
    httpd.serve_forever()
ййй
def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(('localhost', 5000))
        print('Socket server started on port 5000...')
        while True:
            data, addr = server_socket.recvfrom(1024)
            data_dict = json.loads(data.decode())
            with open('storage/data.json', 'w') as file:
                json.dump({data_dict['timestamp']: {'username': data_dict['username'], 'message': data_dict['message']}}, file, indent=2)
                file.write('\n')


if __name__ == '__main__':
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)
    http_thread.start()
    socket_thread.start()
