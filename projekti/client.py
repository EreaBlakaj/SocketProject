import socket
import threading


# Funksioni kryesor i klientit që lidhet me serverin
def client(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    try:
        client_socket.connect((server_ip, server_port))
        print(f"[Lidhur] Klienti është lidhur me serverin {server_ip}:{server_port}")

      
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
           
            message = input("Shkruaj mesazh për serverin ('exit' për të dalë): ")
            if message == 'exit':  
                break
            client_socket.send(message.encode('utf-8'))  #

    except Exception as e:
      
        print(f"[Error] Problem gjatë lidhjes me serverin: {e}")
    finally:
        
        client_socket.close()

if __name__ == "__main__":
   
    server_ip = 'server_ip' 
    server_port = 12345  


    client(server_ip, server_port)
