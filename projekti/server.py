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
            if command == "shutdown":
                log_request(client_ip, "Serveri po mbyllet nga klienti.")
                print(f"[Shutdown] Serveri po mbyllet nga {client_ip}.")
                client_socket.send(b"Serveri po mbyllet me skriptin shutdown.py...\n")
                subprocess.run(["python3", "shutdown.py"])
                client_socket.close()
                for client in clients:
                    client.close()
                break
            #elif command.startswith("kick"):
            #elif command.startswith("broadcast"):
            elif command.startswith("open"):
                file_name = command.split(" ", 1)[1]
                try:
                    with open(file_name, "r") as file:
                        content = file.read()
                        client_socket.send(f"Permbajtja e skedarit {file_name}:\n{content}".encode('utf-8'))
                except FileNotFoundError:
                    client_socket.send(f"Skedari {file_name} nuk u gjet.\n".encode('utf-8'))
                except Exception as e:
                    client_socket.send(f"Gabim gjate hapjes se skedarit: {e}\n".encode('utf-8'))

            else:
                try:
                    exec(command)
                    client_socket.send(b"Komanda u ekzekutua.\n")
                except Exception as e:
                    client_socket.send(f"Error gjate ekzekutimit: {e}\n".encode('utf-8'))

    except Exception as e:
        print(f"[Error] Problem me klientin me qasje te plote: {e}")
    finally:
        client_socket.close()