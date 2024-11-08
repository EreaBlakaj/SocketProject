import socket
import threading
import time
from datetime import datetime
import subprocess

# Variables for IP and port
IP = '' #Server IP
PORT = 12345
MAX_CONNECTIONS = 5
FULL_ACCESS_CLIENTS = [''] #Admin IP
INACTIVITY_TIMEOUT = 120  # 2 minutes inactivity
RESPONSE_TIMEOUT = 12  # 12 seconds response time

clients = []
client_lock = threading.Lock()  # Lock for managing access to clients list

# Logging requests
def log_request(client_ip, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('server_logs.txt', 'a') as log_file:
        log_file.write(f"{timestamp} - IP: {client_ip} - Message: {message}\n")

# Funksioni per dergimin e mesazheve tek te gjithe klientet
def broadcast_message(sender_socket, message):
    with client_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except Exception as e:
                    print(f"[Error] Cannot send message to a client: {e}")

# Funksioni per menaxhimin e klienteve me qasje te plote
def handle_full_access(client_socket, client_address):
    client_ip = client_address[0]
    print(f"[Full Access] {client_ip} ka qasje te plote.")
    log_request(client_ip, "Klienti ka qasje te plote.")
    last_activity = time.time()

    try:
        while True:
            client_socket.send(b"[Prioritet] Komanda: ")
            client_socket.settimeout(INACTIVITY_TIMEOUT)

            try:
                command = client_socket.recv(1024).decode('utf-8')
                last_activity = time.time()
            except socket.timeout:
                client_socket.send(b"Ju jeni joaktiv! A jeni ende aty? (12 sekonda per pergjigje): ")
                client_socket.settimeout(RESPONSE_TIMEOUT)

                try:
                    response = client_socket.recv(1024).decode('utf-8')
                    if response.lower() in ['po', 'yes', 'y']:
                        client_socket.send(b"Faleminderit per pergjigjen!\n")
                        last_activity = time.time()
                        client_socket.settimeout(None)
                        continue
                    else:
                        client_socket.send(b"Lidhja juaj do te mbyllet.\n")
                        break
                except socket.timeout:
                    client_socket.send(b"Ju u larguat per shkak te mungeses se aktivitetit.\n")
                    break
            #if command == "shutdown":
            #elif command.startswith("kick"):
            #elif command.startswith("broadcast"):
            #elif command.startswith("open"):
    except Exception as e:
        print(f"[Error] Problem me klientin me qasje te plote: {e}")
    finally:
        client_socket.close()