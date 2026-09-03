# OSWE Exploit Building Block Plan

## Objective

Turn the existing exploit scripts into a small reusable toolkit of building blocks that can be copied into a final challenge script during the exam.

The goal is not to rewrite every lab into a full framework. The goal is to create a practical library of reusable primitives so each challenge can be finished quickly by assembling the right snippets.

This plan keeps the work focused on:

- fast lab completion,
- copy-pasteable components,
- easy refactoring from monolithic scripts,
- strong separation between shared utilities and lab-specific orchestration.

---

## High-level strategy

Use a two-layer model:

1. Shared building blocks
   - reusable helpers and payloads
   - common web/session/socket logic
   - attack primitives

2. Lab wrappers
   - minimal scripts that call the blocks in order
   - specific to one lab or one challenge flow

This is the sweet spot for OSWE prep. The main script in the exam can stay short while the heavy lifting lives in a library of snippets.

---

## Suggested structure

Create a folder tree like this:

- MASTER/
  - daves_plan.md
  - blocks/
    - common/
      - http_session.py
      - retry.py
      - args.py
      - logging.py
    - web/
      - csrf.py
      - auth.py
      - xss_payloads.py
      - js_exfiltration.py
    - sockets/
      - shell_socket.py
      - websocket_client.py
    - payloads/
      - sqli.py
      - pickle_tokens.py
      - zip_rce.py
      - command_injection.py
    - servers/
      - flask_exfil.py
    - crypto/
      - timestamp_tokens.py
      - md5_bruteforce.py
  - lab_wrappers/
    - ch06_opencrx.py
    - ch07_ws_rce.py
    - ch08_cors.py
    - ch09_fuzzing.py
    - ch11_opencrx.py
    - ch12_sqli_rce.py
    - lab1_xss_admin.py
    - lab2_gallery.py
    - lab3_erka.py
    - lab4_notes.py
    - lab5_chat.py
    - lab6_docedit.py
    - lab7_speakr.py

---

## Suggested source mapping from current scripts

### 1. Common HTTP and retry logic

Source files:
- CH6/script.py
- CH7/script.py
- CH8/script.py
- CH9/script.py
- ch11/script.py
- ch12/script.py
- lab1_answers/script.py
- lab1_answers2/script.py
- lab2_gallery/script.py
- lab3_erka/script.py
- lab4_notes/script.py
- lab5_chat/script.py
- lab6_docedit/script.py
- lab7_speakr/script.py

Use these as the source for:
- build_session
- retry_request
- add_proxy
- parse_args
- print_header
- response handling helpers

These should become shared common helpers rather than duplicated logic inside each lab.

### 2. Flask exfiltration and payload server blocks

Source files:
- CH7/script.py
- lab1_answers/script.py
- lab1_answers2/script.py
- lab5_chat/script.py
- lab7_speakr/script.py

Use these as the source for:
- Flask callback server generator
- XSS JS payload delivery
- cookie and token capture logic
- exfil route patterns

Suggested output block:
- blocks/servers/flask_exfil.py

This is one of the most reusable patterns in the whole set.

### 3. Reverse shell and socket blocks

Source files:
- lab1_answers2/script.py
- lab2_gallery/script.py
- lab4_notes/script.py
- lab5_chat/script.py
- lab6_docedit/script.py
- lab7_speakr/script.py

Use these as the source for:
- socket listen helpers
- run_command wrappers
- shell command execution abstraction
- WebSocket client patterns

Suggested output block:
- blocks/sockets/shell_socket.py
- blocks/sockets/websocket_client.py

### 4. CSRF and auth flow blocks

Source files:
- lab2_gallery/script.py
- lab5_chat/script.py
- lab6_docedit/script.py

Use these as the source for:
- CSRF token extraction
- login flow automation
- registration flow automation
- admin or user takeover after auth

Suggested output block:
- blocks/web/csrf.py
- blocks/web/auth.py

### 5. SQLi primitives

Source files:
- ch12/script.py
- ch12/script2.py
- lab3_erka/script.py
- lab6_docedit/script.py

Use these as the source for:
- boolean SQLi helper functions
- UNION SELECT wrappers
- binary search / substring extraction
- admin ID finding
- field/value extraction

Suggested output block:
- blocks/payloads/sqli.py

This should be a major reusable library because it is a repeated pattern across several labs.

### 6. XSS payloads and JavaScript leakage

Source files:
- lab1_answers/script.py
- lab1_answers2/script.py
- lab5_chat/script.py
- CH8/script.py

Use these as the source for:
- DOM XSS payload generation
- JavaScript callback URLs
- exfiltration URL templates
- cookie/token leakage patterns

Suggested output block:
- blocks/web/xss_payloads.py
- blocks/web/js_exfiltration.py

### 7. Token-generation and password attack helpers

Source files:
- CH6/script.py
- ch11/script.py
- lab1_answers/script.py
- lab1_answers2/script.py

Use these as the source for:
- time-window token generation
- timestamp extraction from server response headers
- Java helper invocation
- password brute force loops

Suggested output block:
- blocks/crypto/timestamp_tokens.py

### 8. Pickle and serialized token abuse

Source files:
- lab7_speakr/script.py
- lab_speakr/script.py

Use these as the source for:
- base64 decode/encode workflow
- pickle payload generation
- user-id mutation in serialized auth values
- exploit payload crafting

Suggested output block:
- blocks/payloads/pickle_tokens.py

### 9. File upload and RCE payload blocks

Source files:
- lab4_notes/script.py
- lab5_chat/script.py
- lab7_speakr/script.py
- ch12/script2.py

Use these as the source for:
- zip upload payloads
- command injection wrappers
- file write or plugin-based RCE
- staged shell execution

Suggested output block:
- blocks/payloads/zip_rce.py
- blocks/payloads/command_injection.py

---

## High-value ordering

If you want to build the toolkit efficiently, do it in this order:

1. common session + retry helpers
2. Flask exfiltration helper
3. shell socket helper
4. CSRF/auth helpers
5. SQLi payload helper
6. timestamp token helper
7. XSS payload helper
8. pickle token helper
9. lab-specific wrappers

This order gives the best payoff early and reduces repeated boilerplate across the entire workspace.

---

## What to keep out of the plan

This plan intentionally does not include copying and pasting snippets into built files. The idea is to create a sourcing scheme and a refactor roadmap.

The user will generate the actual module files and copy them in as needed, but the structure and source mapping are defined here.

---

## Recommended final workflow

When the user is actively exploiting a lab, the intended workflow is:

- open the right helper file,
- copy only the needed function,
- paste into the challenge script,
- patch the target URL, credentials, and ports,
- run and iterate.

This keeps the exam flow fast without requiring a giant permanent framework.

---

## Final recommendation

Build the reusable library around these categories:

- HTTP and session helpers
- shell and socket helpers
- CSRF and auth helpers
- XSS and JS exfil helpers
- SQLi payload helpers
- token generators and brute-force helpers
- pickle and serialized payload helpers
- Flask callback helpers

That gives you a clean, exam-ready exploit stack while staying aligned with the actual patterns found in the current scripts.

---

## Done

This plan is intentionally a source map and blueprint, not a code dump. It tells you where each pattern should be extracted from and which folder each building block belongs in.
