import json
import queue
import threading
import websocket
import time


class DavesSocketManager:
    def __init__(
        self,
        target,
        *,
        headers=None,
        auth_token=None,
        socket_sid=None,
    ):
        self.target = target
        self.headers = headers.copy() if headers else {}
        self.socket = None
        self.auth_token = auth_token
        self.socket_sid = socket_sid
        self.socket_is_live = threading.Event()
        self.socket_queue = queue.Queue()

    def __enter__(self):
        def _run():
            self.socket.run_forever(
                origin=self.target,
                http_proxy_host="127.0.0.1",
                http_proxy_port=8080,
                proxy_type="http",
            )

        self._build_socket()
        socket_thread = threading.Thread(target=_run)
        socket_thread.daemon = True  # Thread dies if main app crashes
        socket_thread.start()
        self.socket_is_live.wait()
        return self

    def _build_socket(self):
        ws_host = self.target.replace("http", "ws")
        url = f"{ws_host}/socket.io/?EIO=3&transport=websocket&sid={self.socket_sid}"
        headers = self.headers
        headers.update({"Cookie": f"io={self.socket_sid}"})

        self.socket = websocket.WebSocketApp(
            url,
            header=headers,
            on_open=self._on_socket_open,
            on_message=self._on_socket_message,
        )

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        time.sleep(0.5)
        if self.socket:
            print("[*] Closing socket connection...")
            self.socket.close()
        self.socket_is_live.clear()

    def _on_socket_open(self, ws):
        print("[+] Socket connected")
        print("[*] Sending confirmation to server...")
        ws.send("5")
        print("[*] Sending canary frame")
        canary_data = {"token": self.auth_token}
        payload = f'42["getDocumentPage",{json.dumps(canary_data)}]'
        self.socket.send(payload)

    def _on_socket_message(self, ws, message):
        if "40" == message:  # Finished connection to namespace
            return
        if "2" == message:  # Ping from server
            return ws.send("3")

        if '"documentPage",' in message and not self.socket_is_live.is_set():
            print(f"[*] Canary frame received: {len(message)}")
            self.socket_is_live.set()
            return

        self.socket_queue.put(message, timeout=5)

    def send(self, event_name, data, *, timeout=60):
        payload = f'42["{event_name}",{json.dumps(data)}]'
        self.socket.send(payload)
        return self.socket_queue.get(timeout=timeout)
