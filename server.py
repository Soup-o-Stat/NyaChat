import socket
import threading
import time
import signal
import sys

clients = {}
server_running = False
server = None
server_password = ""

def cleanup_existing_server():
    global server, clients, server_running
    if server_running:
        server_running = False
    for client in list(clients.keys()):
        try:
            client.close()
        except:
            pass
    clients.clear()
    if server:
        try:
            server.close()
        except:
            pass
    server = None
    print("Cleanup completed")

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
    while server_running:
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

def signal_handler(sig, frame):
    print("\n\nShutting down server...")
    cleanup_existing_server()
    print("Server stopped")
    sys.exit(0)

def start_server():
    global server, server_running
    
    print("Cleaning up previous server instances...")
    cleanup_existing_server()
    time.sleep(1)
    try:
        print("Starting server on port 1234...")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            pass
        server.bind(("0.0.0.0", 1234))
        server.listen()
        server_running = True
        print(f"Server started successfully on port 1234")
        print("Press Ctrl+C to stop server\n")
        while server_running:
            server.settimeout(1.0)
            try:
                client_socket, addr = server.accept()
                threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                if server_running:
                    print(f"Error accepting connection: {e}") 
    except socket.error as e:
        if e.errno == 98:
            print(f"Port 1234 is still busy. Trying to force cleanup...")
            import subprocess
            try:
                subprocess.run(['fuser', '-k', '1234/tcp'], capture_output=True)
                time.sleep(1)
                print("Port forcibly released. Please try starting server again.")
            except:
                print("Could not force release port. Try manually: sudo fuser -k 1234/tcp")
        else:
            print(f"Server error: {e}")
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        cleanup_existing_server()
        print("Server stopped")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        if server_menu():
            start_server()
        else:
            print("Exiting...")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup_existing_server()