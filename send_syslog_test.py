import socket
import sys

def send_syslog(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('utf-8'), (ip, port))
    print(f"Sent to {ip}:{port} -> {message}")

if __name__ == "__main__":
    target_ip = "127.0.0.1"
    target_port = 5140 # Use 5140 for testing if 514 is privileged
    if len(sys.argv) > 1:
        target_port = int(sys.argv[1])
        
    # Mock Cisco config change message
    msg = "<189>29: %SYS-5-CONFIG_I: Configured from console by console"
    send_syslog(target_ip, target_port, msg)
