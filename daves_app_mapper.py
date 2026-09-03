import requests
import concurrent.futures

def master_session():
    session = requests.Session()
    session.verify = False 
    session.trust_env = False 
    session.headers.update({
        "Connection": "close",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    })
    return session

file_name = '/usr/share/wordlists/dirb/small.txt'

def load_targets():
    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()
        lines = content.splitlines()
        print(f"[+] Loaded {len(lines)} action lines.")
        return lines

baseurl = 'http://192.168.228.234/thread/'
def run(targets, tail=""):
    def funct(path):
        url = f"{baseurl}{path}{tail}"
        session = master_session()
        try:
            resp = session.get(url=url, timeout=5)
            if resp.status_code == 401:
                print("~", flush=True, end="")   
            else: 
                # print(resp.status_code, url)\
                None
        except requests.exceptions.Timeout:
            print(url)
            print(".", flush=True, end="")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=300) as ex:
        results = ex.map(funct, targets)
    return filter(lambda x: x is not None, results)
    
def main():
    targets = load_targets()
    targets.append("")
    targets.append("17")
    targets.append("18")
    targets.append("19")
    targets.append("README")
    targets.append("README")
    targets.append("README")
    targets.append("README")
    targets.append("/api/health")
    
    print(f"{len(targets)} targets")  
    results1 = run(targets)     
    print(f"{len(list(results1))} NAUGHT")  
    results2 = run(targets, ".xml")     
    print(f"{len(list(results2))} xml")  
    results3 = run(targets, ".html")     
    print(f"{len(list(results3))} HTML")
    results3 = run(targets, ".md")     
    print(f"{len(list(results3))} md")
    results3 = run(targets, ".php")     
    print(f"{len(list(results3))} php")
    
    
    
if __name__ == "__main__":  
    main()