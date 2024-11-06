import socket
import threading
import time
from datetime import datetime
import subprocess

# Variables for IP and port
IP = '0.0.0.0'
PORT = 12345
MAX_CONNECTIONS = 5
FULL_ACCESS_CLIENTS = ['127.0.0.1']
INACTIVITY_TIMEOUT = 120  # 2 minutes inactivity
RESPONSE_TIMEOUT = 12  # 12 seconds response time

clients = []
client_lock = threading.Lock()  # Lock for managing access to clients list

# Logging requests
def log_request(client_ip, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('server_logs.txt', 'a') as log_file:
        log_file.write(f"{timestamp} - IP: {client_ip} - Message: {message}\n")

