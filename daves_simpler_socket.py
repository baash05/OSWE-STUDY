import json
import threading
import time

import websocket


class DavesSimplerSocket:
    def __init__(self, target, *, headers=None, auth_token=None, socket_sid=None):
        self.target = target
        self.headers = headers.copy() if headers else {}
        self.auth_token = auth_token
        self.socket_sid = socket_sid
        self.socket = None
        self.socket_is_live = threading.Event()

    def __enter__(self):
        self._build_socket()
        self.socket.run_forever(
            origin=self.target,
            http_proxy_host="127.0.0.1",
            http_proxy_port=8080,
            proxy_type="http",
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        time.sleep(0.5)
        if self.socket:
            self.socket.close()
        self.socket_is_live.clear()

    def _build_socket(self):
        ws_host = self.target.replace("http", "ws")
        url = f"{ws_host}/socket.io/?EIO=3&transport=websocket&sid={self.socket_sid}"

        request_headers = dict(self.headers)
        if self.socket_sid:
            existing_cookie = request_headers.get("Cookie", "")
            cookie_values = [part for part in [existing_cookie, f"io={self.socket_sid}"] if part]
            request_headers["Cookie"] = "; ".join(cookie_values)

        header_list = [f"{key}: {value}" for key, value in request_headers.items()]

        self.socket = websocket.WebSocketApp(
            url,
            header=header_list,
            on_open=self._on_socket_open,
            on_message=self._on_socket_message,
        )

    def _on_socket_open(self, ws):
        print("[+] Socket connected")
        print("[*] Sending confirmation to server...")
        ws.send("5")
        print("[*] Sending canary frame")
        canary_data = {"token": self.auth_token}
        payload = f'42["getDocumentPage",{json.dumps(canary_data)}]'
        ws.send(payload)

    def _on_socket_message(self, ws, message):
        if message == "40":
            return
        if message == "2":
            ws.send("3")
            return

        if '"documentPage",' in message and not self.socket_is_live.is_set():
            print(f"[*] Canary frame received: {len(message)}")
            self.socket_is_live.set()
            return

        return message

    def send(self, event_name, data, *, timeout=60):
        if self.socket is None:
            raise RuntimeError("Socket is not open")

        payload = f'42["{event_name}",{json.dumps(data)}]'
        self.socket.send(payload)
        return self.socket.recv()
