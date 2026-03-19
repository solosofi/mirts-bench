import json
from http.server import BaseHTTPRequestHandler, HTTPServer

import kaggle_benchmarks as kbench


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._send_json({"ok": True})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/prompt":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        data = json.loads(body.decode("utf-8"))
        prompt = data.get("prompt", "")
        model = data.get("model")

        llm = kbench.llm if not model else kbench.llms[model]
        response = llm.prompt(prompt)

        self._send_json({"content": response})

    def _send_json(self, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Kaggle bridge listening on http://0.0.0.0:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
