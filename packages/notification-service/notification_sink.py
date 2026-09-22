from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        print(body.decode(errors="replace"), flush=True)
        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


if __name__ == "__main__":
    """
    This is a simple HTTP server that receives notifications from the notification-service and prints them to the console.
    It is used to test the notification-service without having to deploy it to a real server.
    """
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
