#!/usr/bin/env python3
"""Quick RTSP scanner that finds streams and saves selected link with optional credentials."""
import argparse, getpass, ipaddress, socket
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_PATHS = ["", "/live", "/h264", "/stream", "/0"]
SELECTED_FILE = Path("selected_rtsp.txt")


def rtsp_ok(ip, port, path, timeout):
    try:
        s = socket.create_connection((ip, port), timeout)
        req = f"OPTIONS rtsp://{ip}{path} RTSP/1.0\r\nCSeq: 1\r\n\r\n".encode()
        s.send(req)
        return b"200" in s.recv(256)
    except: return False


def scan(net, port, paths, timeout):
    print(f"[*] Scanning {net}…")
    found = []
    with ThreadPoolExecutor(500) as exec:
        futs = [exec.submit(rtsp_ok, str(ip), port, p, timeout)
                for ip in ipaddress.ip_network(net).hosts()
                for p in paths]
        for f in as_completed(futs):
            if f.result():
                ip = f._args[0]
                path = f._args[2]
                url = f"rtsp://{ip}{path}"
                print(f"[+] {url}")
                found.append(url)
    return found


def pick_and_save(urls):
    if not urls: return print("No streams found.")
    for i, u in enumerate(urls): print(f"[{i}] {u}")
    i = input("Select stream #: ").strip()
    if not i.isdigit() or not (0 <= int(i) < len(urls)): return
    u, user, pwd = urls[int(i)], input("User: "), getpass.getpass("Pass: ")
    if user: u = u.replace("rtsp://", f"rtsp://{quote(user)}:{quote(pwd)}@")
    SELECTED_FILE.write_text(u + "\n")
    print(f"Saved: {u}")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("-n", default="192.168.1.0/24")
    a.add_argument("-p", type=int, default=554)
    a.add_argument("-t", type=float, default=2)
    args = a.parse_args()
    pick_and_save(scan(args.n, args.p, DEFAULT_PATHS, args.t))


if __name__ == "__main__":
    main()
