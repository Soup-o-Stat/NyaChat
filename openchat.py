import socket
import threading

def listen(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print("\n" + msg)
        except:
            break

server_ip = input("IP: ")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, 24))

threading.Thread(target=listen, args=(sock,), daemon=True).start()

while True:
    message = input()
    if message.lower() == "/quit":
        break
    sock.send(message.encode())

sock.close()