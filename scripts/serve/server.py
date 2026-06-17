# -*- coding: utf-8 -*-
"""启动热点图展示用的本地静态服务器。

用法：
    python scripts/serve/server.py
    python scripts/serve/server.py --tunnel

带 --tunnel 时会尝试使用 工具/cloudflared-windows-386.exe 创建临时外网访问链接。
按 Ctrl+C 停止服务。
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT
DEFAULT_TARGET = "热点图展示/澳门生物多样性热点图.html"
HOST = "0.0.0.0"
DEFAULT_PORT = 8080


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        if args and ("404" in str(args[0]) or "500" in str(args[0])):
            sys.stderr.write(f"  HTTP {args[0]}\n")


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"


def find_cloudflared() -> str | None:
    candidates = [
        ROOT / "工具" / "cloudflared-windows-386.exe",
        ROOT / "工具" / "cloudflared.exe",
        ROOT / "cloudflared-windows-386.exe",
    ]
    for path in candidates:
        if path.is_file():
            return str(path)
    return shutil.which("cloudflared")


def start_cloudflared(port: int) -> subprocess.Popen[str] | None:
    exe = find_cloudflared()
    if not exe:
        print("\n未找到 cloudflared，仅提供本地访问。")
        return None

    print(f"使用 cloudflared：{Path(exe).name}")
    try:
        return subprocess.Popen(
            [exe, "tunnel", "--url", f"http://localhost:{port}", "--no-autoupdate"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except FileNotFoundError:
        print("cloudflared 无法执行，仅提供本地访问。")
        return None


def read_tunnel_url(proc: subprocess.Popen[str], ready_event: threading.Event) -> None:
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
    if proc.stdout is None:
        return
    for raw_line in proc.stdout:
        line = raw_line.strip()
        if not line:
            continue
        match = url_pattern.search(line)
        if match:
            ready_event.public_url = match.group(0)  # type: ignore[attr-defined]
            ready_event.set()
        if "ERR " in line or "error" in line.lower():
            sys.stderr.write(f"  [cloudflared] {line}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="启动热点图展示用的静态服务器。")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="本地服务端口。")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="打开的页面路径。")
    parser.add_argument("--tunnel", action="store_true", help="使用 cloudflared 生成临时外网链接。")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器。")
    args = parser.parse_args()

    target = args.target.replace("\\", "/")
    target_path = ROOT / target
    if not target_path.exists():
        raise SystemExit(f"未找到页面：{target_path}")

    handler = functools.partial(QuietHandler, directory=str(WEB_DIR))
    server = http.server.ThreadingHTTPServer((HOST, args.port), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    local_ip = get_local_ip()
    local_url = f"http://localhost:{args.port}/{target}"
    print("=" * 60)
    print("澳门生物多样性数据地图 - 本地服务器")
    print("=" * 60)
    print(f"项目根目录：{ROOT}")
    print(f"本机访问：{local_url}")
    if local_ip != "127.0.0.1":
        print(f"局域网访问：http://{local_ip}:{args.port}/{target}")

    tunnel_proc = None
    if args.tunnel:
        tunnel_proc = start_cloudflared(args.port)
        if tunnel_proc:
            ready_event = threading.Event()
            ready_event.public_url = None  # type: ignore[attr-defined]
            tunnel_thread = threading.Thread(target=read_tunnel_url, args=(tunnel_proc, ready_event), daemon=True)
            tunnel_thread.start()
            print("等待外网隧道就绪，最长约 60 秒...")
            if ready_event.wait(timeout=60):
                public_url = ready_event.public_url  # type: ignore[attr-defined]
                public_page = f"{public_url}/{target}"
                print(f"外网访问：{public_page}")
                if not args.no_browser:
                    webbrowser.open(public_page)
            else:
                print("外网隧道建立超时，继续保留本地访问。")

    if not args.no_browser and not args.tunnel:
        webbrowser.open(local_url)

    print("\n按 Ctrl+C 停止服务。")
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        server.shutdown()
        if tunnel_proc:
            tunnel_proc.terminate()
            try:
                tunnel_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel_proc.kill()
        print("服务已停止。")


if __name__ == "__main__":
    main()
