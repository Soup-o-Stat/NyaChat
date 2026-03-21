import socket
import threading

clients=[]

def handle_client(client_socket, addr):
    print(f"{addr} conected")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            for c in clients:
                if c != client_socket:
                    c.send(f"{addr}: {message}".encode())
        except:
            break
    print(f"{addr} disconected")
    clients.remove(client_socket)
    client_socket.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 24))
server.listen()
print("Server started. Port - 24")

while True:
    client_socket, addr = server.accept()
    clients.append(client_socket)
    threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()