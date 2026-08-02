import os.path
import socket
import threading
import sys
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 4000))
sock.settimeout(5.0)

cmds_docs: list[tuple[str, str]] = [
    ("help", "It returns a commands list with their descriptions"),
    ("exit", "It exits the program"),
    ("get_messages", "It shows you the messages and the player who sent it"),
]

if os.path.exists("messages.json"):
    with open("messages.json", "r") as f:
        messages = json.load(f)
elif not os.path.exists("messages.json"):
    messages: list[tuple[str, str]] = []

stop_signal = threading.Event()


def save_messages():
    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=4)


def cmds():
    while not stop_signal.is_set():
        command = input("Enter a command: ")
        if command.lower() == "help":
            for cmd, description in cmds_docs:
                print(f'Command: "{cmd}" | Description: {description}')
        if command.lower() == "exit":
            save_messages()
            stop_signal.set()
            sock.close()
        if command.lower() == "get_messages":
            for person, message in messages:
                print(f'{person}: "{message}"')
        if command.lower() == "clear_messages":
            messages.clear()
            print("Messages cleared")
        if command.lower().startswith("purge"):
            purge_ammount = int(command.lower().replace("purge", "").strip())
            del messages[-purge_ammount:]


threading.Thread(target=cmds, daemon=True).start()

while not stop_signal.is_set():
    try:
        data, addr = sock.recvfrom(4096)
        decoded_msg = data.decode()

        if decoded_msg == "GET_MESSAGES":
            messages_json = json.dumps(messages).encode()
            sock.sendto(messages_json, addr)
        else:
            try:
                user_message_json: dict[str, str] = json.loads(decoded_msg)
                if user_message_json.get("message") is not None:
                    messages.append(
                        (user_message_json["username"], user_message_json["message"])
                    )
            except json.JSONDecodeError:
                continue
    except (TimeoutError, OSError, ConnectionRefusedError):
        continue
