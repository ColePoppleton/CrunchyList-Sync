import webbrowser
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

CLIENT_ID = "34167"
REDIRECT_URI = "http://localhost:3000/callback"
PORT = 3000


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    token_container = {}

    def do_GET(self):
        if self.path.startswith("/callback"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html = """
            <html>
            <body>
                <h1>Login Successful!</h1>
                <p>You can close this tab and return to the app.</p>
                <script>
                    const hash = window.location.hash.substring(1);
                    const params = new URLSearchParams(hash);
                    const token = params.get('access_token');
                    if (token) {
                        fetch('/save_token', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({token: token})
                        });
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)

    def do_POST(self):
        if self.path == "/save_token":
            length = int(self.headers.get('content-length'))
            data = self.rfile.read(length)
            import json
            token_data = json.loads(data)
            self.token_container['token'] = token_data.get('token')
            self.send_response(200)
            self.end_headers()
            threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        return


def start_login_flow(on_success_callback):
    token_container = {}

    server = HTTPServer(('localhost', PORT), OAuthCallbackHandler)
    server.RequestHandlerClass.token_container = token_container
    auth_url = (
        f"https://anilist.co/api/v2/oauth/authorize?"
        f"client_id={CLIENT_ID}&response_type=token"
    )
    webbrowser.open(auth_url)

    try:
        server.serve_forever()
    except:
        pass

    server.server_close()

    token = token_container.get('token')
    if token:
        on_success_callback(token)
        return True
    return False