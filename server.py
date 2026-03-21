import socket
import threading
import time
import signal
import sys
import subprocess

clients = {}
server = None
server_password = ""

def broadcast(message, exclude=None):
    for client in list(clients.keys()):
        if client != exclude:
            try:
                client.send(message.encode())
            except:
                pass

def handle_client(client_socket, addr):
    global clients
    if server_password:
        try:
            client_socket.send("[SYSTEM] Enter server password: ".encode())
            password = client_socket.recv(1024).decode().strip()
            if password != server_password:
                client_socket.send("[SYSTEM] Wrong password, disconnecting.".encode())
                client_socket.close()
                return
            else:
                client_socket.send("[SYSTEM] Password OK".encode())
        except:
            return
    nickname = str(addr)
    try:
        first_msg = client_socket.recv(1024).decode()
        if first_msg.startswith("/nick"):
            nickname = first_msg.split(" ", 1)[1]
    except:
        pass
    clients[client_socket] = nickname
    broadcast(f"[SYSTEM] {nickname} joined the chat")
    print(f"{nickname} joined the chat")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            if message.strip().lower() == "/list":
                user_list = "\n".join(clients.values())
                client_socket.send(f"[SYSTEM] Online users ({len(clients)}):\n{user_list}".encode())
                continue
            broadcast(f"{nickname}: {message}", exclude=client_socket)
        except:
            break
    if client_socket in clients:
        del clients[client_socket]
    client_socket.close()
    broadcast(f"[SYSTEM] {nickname} left the chat")
    print(f"{nickname} left the chat")

def server_menu():
    global server_password
    while True:
        print("\n=== Server Menu ===")
        print("1 - Start server")
        print("2 - Set password")
        print("0 - Exit")
        choice = input(">> ")
        if choice == "1":
            return True
        elif choice == "2":
            server_password = input("Enter new server password (empty = no password): ").strip()
            print("Password updated")
        elif choice == "0":
            return False

def start_server():
    global server

    print("Cleaning up port 1234...")
    try:
        subprocess.run(['fuser', '-k', '1234/tcp'], capture_output=True)
        time.sleep(1)
    except:
        pass
    try:
        print("Starting server on port 1234...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 1234))
        server.listen()
        print(f"Server started successfully on port 1234")
        print("Press Ctrl+C to stop server\n")
        while True:
            server.settimeout(1.0)
            try:
                client_socket, addr = server.accept()
                threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error: {e}") 
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        if server:
            server.close()
        for client in list(clients.keys()):
            try:
                client.close()
            except:
                pass
        clients.clear()
        print("Server stopped")

if __name__ == "__main__":
    if server_menu():
        start_server()