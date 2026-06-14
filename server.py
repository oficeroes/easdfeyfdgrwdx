"""
============================================================
澳门生物多样性地图 — 本地静态服务器 + Cloudflare Tunnel
============================================================
用法：
  python server.py              → 仅本地访问
  python server.py --tunnel     → 本地 + 外网（cloudflared）

外网访问需要一个 Cloudflare 账号，首次使用需在浏览器中授权。
cloudflared 下载: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

按 Ctrl+C 停止所有服务
============================================================
"""

import http.server
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import webbrowser

# ===== 配置 =====
PORT = 8080
HOST = '0.0.0.0'         # 绑定所有网卡（局域网 + cloudflared 都需要）
TARGET = '热点图展示/澳门生物多样性热点图.html'

# ===== 切换到项目根目录 =====
root_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(root_dir)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """静默模式 HTTP 处理器"""

    def log_message(self, format, *args):
        if '404' in str(args) or '500' in str(args):
            sys.stderr.write(f'  ✗ {args[0]}\n')


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def find_cloudflared() -> str | None:
    """查找 cloudflared 可执行文件"""
    # 1) 当前目录
    for name in ['cloudflared-windows-386.exe', 'cloudflared.exe', 'cloudflared']:
        path = os.path.join(root_dir, name)
        if os.path.isfile(path):
            return path
    # 2) PATH 中
    found = shutil.which('cloudflared')
    if found:
        return found
    return None


def start_cloudflared(port: int) -> subprocess.Popen | None:
    """启动 cloudflared 隧道，返回进程对象"""
    exe = find_cloudflared()
    if not exe:
        print('\n  ⚠️  未找到 cloudflared，仅提供本地访问')
        print('     下载: https://developers.cloudflare.com/cloudflare-one/'
              'connections/connect-networks/downloads/')
        return None

    print(f'  🔑 使用 cloudflared: {os.path.basename(exe)}')
    print(f'  🌍 正在建立外网隧道...')

    try:
        proc = subprocess.Popen(
            [exe, 'tunnel', '--url', f'http://localhost:{port}',
             '--no-autoupdate'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
        )
        return proc
    except FileNotFoundError:
        print('\n  ⚠️  cloudflared 无法执行')
        return None


def read_tunnel_url(proc: subprocess.Popen, ready_event: threading.Event):
    """实时读取 cloudflared 输出，提取公网 URL"""
    url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com')

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue

        # 提取公网 URL
        match = url_pattern.search(line)
        if match:
            ready_event.public_url = match.group(0)
            ready_event.set()

        # 打印 cloudflared 状态行（简洁模式）
        if 'ERR ' in line or 'error' in line.lower():
            sys.stderr.write(f'  [cloudflared] {line}\n')
        elif 'INF ' in line:
            # 只打印关键信息行
            if any(kw in line for kw in ['Created', 'Requesting', 'Registered',
                                          'connection', 'trycloudflare']):
                print(f'  [cloudflared] {line}')


def main():
    use_tunnel = '--tunnel' in sys.argv

    # 检查目标文件
    if not os.path.exists(TARGET):
        print(f'⚠️  未找到 {TARGET}')
        sys.exit(1)

    local_ip = get_local_ip()

    # ===== 打印信息 =====
    print('=' * 60)
    print('  🦜  澳门生物多样性数据地图 — 本地服务器')
    print('=' * 60)
    print(f'\n  📁 根目录: {root_dir}')
    print(f'\n  🌐 本机访问:')
    print(f'     http://localhost:{PORT}/{TARGET}')
    if local_ip != '127.0.0.1':
        print(f'\n  📱 局域网访问:')
        print(f'     http://{local_ip}:{PORT}/{TARGET}')

    # ===== 启动 HTTP 服务器（后台线程）=====
    server = http.server.HTTPServer((HOST, PORT), QuietHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f'\n  ✅ HTTP 服务器已启动 (端口 {PORT})')

    # ===== cloudflared 隧道 =====
    tunnel_proc = None
    tunnel_thread = None
    ready_event = threading.Event()
    ready_event.public_url = None

    if use_tunnel:
        tunnel_proc = start_cloudflared(PORT)
        if tunnel_proc:
            tunnel_thread = threading.Thread(
                target=read_tunnel_url,
                args=(tunnel_proc, ready_event),
                daemon=True,
            )
            tunnel_thread.start()

    # ===== 等待公网 URL 或直接打开本地 =====
    if tunnel_proc:
        print(f'  ⏳ 等待外网隧道就绪（首次可能需要浏览器授权）...\n')
        print('=' * 60)

        # 等待最多 45 秒
        if ready_event.wait(timeout=60):
            public_url = ready_event.public_url
            print(f'\n  🌍 外网访问链接:')
            print(f'     {public_url}/{TARGET}')
            print(f'\n  📋 将上面链接分享给任何人即可访问！')
            webbrowser.open(f'{public_url}/{TARGET}')
        else:
            print('\n  ⚠️  隧道建立超时，仅本地可用')
            print('     请检查 cloudflared 是否已安装并登录')
            webbrowser.open(f'http://localhost:{PORT}/{TARGET}')
    else:
        print('=' * 60)
        webbrowser.open(f'http://localhost:{PORT}/{TARGET}')

    print(f'\n  ⏹  按 Ctrl+C 停止所有服务\n')

    # ===== 等待中断 =====
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print('\n\n  🧹 正在清理...')
        server.shutdown()
        if tunnel_proc:
            tunnel_proc.terminate()
            try:
                tunnel_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                tunnel_proc.kill()
        print('  👋 所有服务已停止')
        sys.exit(0)


if __name__ == '__main__':
    main()
