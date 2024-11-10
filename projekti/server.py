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
              elif command.startswith("kick"):
                target_ip = command.split(" ")[1]
                with client_lock:
                    for client in clients:
                        if client.getpeername()[0] == target_ip:
                            client.send(b"Ju u larguat nga serveri.")
                            client.close()
                            clients.remove(client)
                            print(f"[Kick] {target_ip} u largua nga serveri nga {client_ip}.")
                            log_request(client_ip, f"Largoi klientin {target_ip}.")
                            break

            elif command.startswith("broadcast"):
                # Mesazh per te derguar tek te gjithe klientet
                message = command.split(" ", 1)[1]  # Mesazhi pas komandes "broadcast"
                broadcast_message(client_socket, f"[Broadcast nga {client_ip}]: {message}")
                client_socket.send(b"Mesazhi u broadcastua tek te gjithe klientet.\n")

            else:
                try:
                    exec(command)
                    client_socket.send(b"Komanda u ekzekutua.\n")
                except Exception as e:
                    client_socket.send(f"Error gjate ekzekutimit: {e}\n".encode('utf-8'))
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
        # Funksioni per klientet me vetem qasje leximi (me vonese dhe monitorim te inaktivitetit)
def handle_read_only(client_socket, client_address):
    client_ip = client_address[0]
    print(f"[Read Only] {client_ip} ka vetem qasje per lexim.")
    log_request(client_ip, "Klienti ka vetem qasje per lexim.")
    last_activity = time.time()

    try:
        while True:
            time.sleep(2)  # Vonesa per klientet me vetem qasje leximi
            client_socket.settimeout(INACTIVITY_TIMEOUT)

            try:
                message = client_socket.recv(1024).decode('utf-8')
                last_activity = time.time()  # Rifresko kohen e fundit te aktivitetit
            except socket.timeout:
                # Klienti ka qene joaktiv per 2 minuta
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

            client_socket.send(b"Keni vetem qasje per lexim.\n")

    except Exception as e:
        print(f"[Error] Problem me klientin me qasje vetem per lexim: {e}")
    finally:
        client_socket.close()

# Funksioni per te krijuar serverin dhe pranuar lidhje te reja
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(MAX_CONNECTIONS)
    print(f"[Startuar] Serveri eshte duke degjuar ne {IP}:{PORT}")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            with client_lock:
                clients.append(client_socket)

            if client_address[0] in FULL_ACCESS_CLIENTS:
                client_thread = threading.Thread(target=handle_full_access, args=(client_socket, client_address))
            else:
                client_thread = threading.Thread(target=handle_read_only, args=(client_socket, client_address))

            client_thread.start()
        except Exception as e:
            print(f"[Error] Problem me serverin: {e}")

if __name__ == "__main__":
    start_server()