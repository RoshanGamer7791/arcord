"""
Date created (dd/mm/yy): 06/11/26
Author: Roshan
License: MIT
"""

import socket
import json
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 8653))
sock.settimeout(5.0)

cmd_docs: list[tuple[str, str]] = [
    ("help", "Prints all the commands and their definitions"),
    ("exit", "Exits the program"),
    ("purge", "purge <amount> purges the amount of messages you want")
]


connected_ips: list[tuple[str, tuple[str, int]]] = []
messages: list[tuple[str, str]] = []

def handle_commands():
    while True:
        cmd = input("Enter a command: ")
        match cmd.lower():
            case "help":
                for name, definition in cmd_docs:
                    print(f"{name}: {definition}")
            case "exit":
                stop_event.set()
                break
            case "purge":
                stop_index = int(cmd.lower().split()[1])
                del messages[0:-stop_index]


stop_event = threading.Event()
threading.Thread(target=handle_commands).start()

while not stop_event.is_set():
    try:
        data, addr = sock.recvfrom(65536)
        jsonData: dict = json.loads(data)
        if jsonData["type"] == "con":
            connected_ips.append((jsonData["username"], addr))
            messages.append(("Server", f"{jsonData["username"]} has came online"))
        if jsonData["type"] == "dis":
            connected_ips.remove((jsonData["username"], addr))
            messages.append(("Server", f"{jsonData["username"]} has came offline"))
        if jsonData["type"] == "GET":
            if jsonData["request"] == "messages":
                sock.sendto(json.dumps(messages).encode("utf-8"), addr)
            if jsonData["request"] == "online_users":
                sock.sendto(json.dumps([connected_ip[0] for connected_ip in connected_ips]).encode("utf-8"), addr)
        if jsonData["type"] == "POST":
            if jsonData["request"] == "message":
                messages.append((jsonData["username"], jsonData["message"]))
    except TimeoutError:
        continue
    except OSError:
        break
