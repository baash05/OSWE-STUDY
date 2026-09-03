import subprocess

def build_tokens_with_java(start_time, end_time):
    print("[*] Compile the javascript")
    subprocess.run(["javac", "OpenCRXtoken.java"], check=True)
    print("[+] Compiled.. we hope")
    result = subprocess.run(
        ["java", "OpenCRXtoken", f"{start_time}", f"{end_time}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


if "__main__" == __name__:
    start_time = 1783036227142
    end_time = 1783036227585
    tokens = build_tokens_with_java(start_time, end_time)
    print(f"Tokens: {tokens}")