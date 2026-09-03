import argparse
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
STATE = argparse.Namespace(local_text=None, proof_text=None)
PROXIES = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}

def build_session():
    session = requests.Session()
    session.verify = False
    session.trust_env = False
    session.headers.update(
        {
            "Connection": "close",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }
    )
    session.proxies = PROXIES
    return session


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--laddr", required=True)
    parser.add_argument("--lport", required=True, type=int)
    parser.add_argument("--username", default="daveisawesome")
    parser.add_argument("--password", default="testtest")
    return parser.parse_args()


def print_header(msg):
    print("")
    print("=" * 42)
    print(f"=\t{msg}")
    print("=" * 42)


def retry_request(func, retries=3, delay=0.1):
    try:
        return func()
    except requests.exceptions.RequestException as e:
        if retries - 1:
            time.sleep(delay)
            return retry_request(func, retries - 1, delay)
        else:
            raise

def main(args):
    print_header("STARTING EXPLOIT 1")

if "__main__" == __name__:
    args = get_args()
    main(args)
    print_header("EXPLOIT 1 COMPLETE")
    print(f"[+] The local text is: {STATE.local_text}")
    print(f"[+] The proof text is: {STATE.proof_text}")