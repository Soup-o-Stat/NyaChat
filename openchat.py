import socket
import threading
import json
import os
import winsound
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

CONFIG_FILE = "config.json"
SOUND_FILE = "sounds//received.wav"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"ip": "", "nickname": "anon", "password": ""}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def play_sound():
    try:
        winsound.PlaySound(SOUND_FILE, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except:
        pass

def listen(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(msg)
                play_sound()
        except:
            break

def connect_to_server(config):
    if not config["ip"]:
        print("IP is not set")
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((config["ip"], 1234))
    except:
        print("Couldn't connect")
        return
    try:
        initial_msg = sock.recv(1024).decode()
        if initial_msg.startswith("[SYSTEM] Enter server password:"):
            sock.send(config.get("password", "").encode())
            resp = sock.recv(1024).decode()
            if "Wrong password" in resp:
                print(resp)
                sock.close()
                return
    except:
        pass
    sock.send(f"/nick {config['nickname']}".encode())
    threading.Thread(target=listen, args=(sock,), daemon=True).start()
    print(f"Connected as {config['nickname']}")
    session = PromptSession("> ")
    with patch_stdout():
        while True:
            try:
                message = session.prompt()
            except KeyboardInterrupt:
                break
            if message.lower() == "/exit":
                break
            sock.send(message.encode())
            if message.lower() == "/help":
                print("\n/help - commands\n/list - users\n/exit - exit\n")
    sock.close()

def settings_menu(config):
    print("=== Settings ===")
    ip = input("Enter server IP: ")
    nickname = input("Enter your nickname: ")
    password = input("Enter server password (if any): ")
    config["ip"] = ip
    config["nickname"] = nickname
    config["password"] = password
    save_config(config)
    print("Saved!")

def main():
    config = load_config()
    while True:
        print("\n=== OpenChat ===")
        print("1 - Connect")
        print("2 - Settings")
        print("0 - Exit")
        choice = input(">> ")
        if choice == "1":
            connect_to_server(config)
        elif choice == "2":
            settings_menu(config)
            config = load_config()
        elif choice == "0":
            break
        else:
            print("Error")

if __name__ == "__main__":
    main()