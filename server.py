import socket
import threading

clients = {}
server_running = True
server = None

def broadcast(message, exclude=None):
    for client in list(clients.keys()):
        if client != exclude:
            try:
                client.send(message.encode())
            except:
                pass

def handle_client(client_socket, addr):
    global clients
    nickname = str(addr)
    try:
        first_msg = client_socket.recv(1024).decode()
        if first_msg.startswith("/nick"):
            nickname = first_msg.split(" ", 1)[1]
    except:
        pass
    clients[client_socket] = nickname
    print(f"{nickname} connected")
    broadcast(f"[SYSTEM] {nickname} joined the chat")
    while server_running:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            if message.strip().lower() == "/list":
                user_list = "\n".join(clients.values())
                client_socket.send(
                    f"[SYSTEM] Online users ({len(clients)}):\n{user_list}".encode()
                )
                continue
            broadcast(f"{nickname}: {message}", exclude=client_socket)
        except:
            break
    print(f"{nickname} disconnected")
    if client_socket in clients:
        del clients[client_socket]
    client_socket.close()
    broadcast(f"[SYSTEM] {nickname} left the chat")

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 1234))
    server.listen()
    server.settimeout(1)
    print("Server started. Port - 1234")
    while server_running:
        try:
            client_socket, addr = server.accept()
            threading.Thread(
                target=handle_client,
                args=(client_socket, addr),
                daemon=True
            ).start()
        except socket.timeout:
            continue

except KeyboardInterrupt:
    print("\nShutting down server...")
    server_running = False

finally:
    print("Closing connections...")

    for c in list(clients.keys()):
        try:
            c.close()
        except:
            pass
    if server:
        try:
            server.close()
        except:
            pass

    print("Server stopped")