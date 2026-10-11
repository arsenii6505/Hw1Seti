import os
import subprocess
import tempfile
import time
from urllib.parse import urlencode

from requests import Session
from my.Hw1Seti.ParsedRequest import ParsedRequest

def get_as_requests(parsed_request: ParsedRequest) -> str:
    return session.request(
        parsed_request.method,
        base_url + parsed_request.additional_path,
        headers=parsed_request.headers,
        cookies=parsed_request.cookies,
        data=parsed_request.data,
        files=parsed_request.files,
        params=parsed_request.params
    ).text

def get_as_curl(parsed_req: ParsedRequest) -> str:
    url = base_url + parsed_req.additional_path

    if parsed_req.params:
        separator = "&" if "?" in url else "?"
        url += separator + urlencode(parsed_req.params)

    cmd = ["curl", "-s", "-S", "-X", parsed_req.method.upper()]

    for key, value in parsed_req.headers.items():
        cmd += ["-H", f"{key}: {value}"]

    if parsed_req.cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in parsed_req.cookies.items())
        cmd += ["-b", cookie_str]

    for key, value in parsed_req.data.items():
        cmd += ["--data", f"{key}={value}"]

    tmp_files = []  # чтобы потом удалить

    try:
        # Файлы: пишем содержимое во временные файлы
        for field, file_info in parsed_req.files.items():
            # file_info может быть:
            #   - (filename, content)  где content: bytes или str
            #   - просто content (тогда имя поля = field)
            if isinstance(file_info, tuple) and len(file_info) == 2:
                filename, content = file_info
            else:
                filename, content = field, file_info

            if isinstance(content, str):
                content = content.encode("utf-8")

            # suffix помогает curl угадать mime-type по расширению
            suffix = os.path.splitext(filename)[1] or ".bin"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp.write(content)
            tmp.close()
            tmp_files.append(tmp.name)

            # ;filename=... — чтобы на сервере имя файла было правильным
            cmd += ["-F", f"{field}=@{tmp.name};filename={filename}"]

        cmd.append(url)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                text=True,
            )
        except subprocess.TimeoutExpired:
            return ""

        if result.returncode != 0 and not result.stdout:
            return result.stderr

        return result.stdout

    finally:
        # Чистим временные файлы в любом случае
        for path in tmp_files:
            try:
                os.unlink(path)
            except OSError:
                pass

token = "064f1bd0eb94d3d18ba2b2c772e827ce"
base_url = "http://hw1.alexbers.com"
send_type = "requests"
step = 0
prev_text = ""
prev_request = ParsedRequest()
prev_request.cookies["user"] = token
session = Session()
session.trust_env = False
while True:
    time.sleep(1)
    request_text = ""
    if send_type == "requests":
        request_text = get_as_requests(prev_request)
    elif send_type == "curl":
        request_text = get_as_curl(prev_request)
    else:
        raise ValueError("Unknown send type method")
    session.cookies.clear()
    if "Секрет" in request_text:
        print("WELL DONE")
        print(request_text)
        break
    parsed_request = ParsedRequest.parse(request_text)
    parsed_request.cookies["user"] = token
    if step + 1 != parsed_request.step:
        print("ERROR")
        print(prev_text)
        print("method:", prev_request.method)
        print("path:", prev_request.additional_path)
        print("headers:", prev_request.headers)
        print("cookies:", prev_request.cookies)
        print("params:", prev_request.params)
        print("files:", prev_request.files)
        print("data:", prev_request.data)
        print("step:", prev_request.step)
        print("texts:")
        for i in prev_request.texts:
            print("  ", i)
        break
    prev_text = request_text
    prev_request = parsed_request
    step += 1
    print("Шаг", step)

