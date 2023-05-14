import http.server
import socketserver
from functools import partial
from pathlib import Path
import re

VIZ_DIR = Path(__file__).parent / "interactive_viz_template"


class MeetupVizHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, runName: str, *args, **kwargs):
        self.runDir = Path(runName)
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/":
            self.handle_index()
            return

        if re.search("/data/*", self.path):
            self.handle_data_request()
            return

        self.try_handle_viz_code_request()

    def handle_404(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        response = f"<html><head></head><body>Page not found</body></html>"
        self.wfile.write(bytes(response, "utf8"))

    def handle_data_request(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        filePath = self.runDir / self.path.replace("/data/", "")
        with open(filePath, "r") as file:
            contents = file.read()
            self.wfile.write(bytes(contents, "utf8"))

    def handle_index(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(VIZ_DIR / "index.html", "rb") as file:
            self.wfile.write(file.read())

    def try_handle_viz_code_request(self):
        filePath = VIZ_DIR / Path(self.path[1:])
        if filePath.exists():
            self.send_response(200)
            match filePath.suffix:
                case ".js":
                    self.send_header("Content-type", "application/javascript")
                case ".html":
                    self.send_header("Content-type", "text/html")
                case ".css":
                    self.send_header("Content-type", "text/css")
                case _:
                    self.send_header("Content-type", "text/html")

            self.end_headers()
            with open(filePath, "rb") as file:
                self.wfile.write(file.read())

        else:
            self.handle_404()


class MyServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_server(runName: str):
    handler_object = partial(MeetupVizHTTPRequestHandler, runName)

    PORT = 8000
    my_server = MyServer(("", PORT), handler_object)

    my_server.serve_forever()
