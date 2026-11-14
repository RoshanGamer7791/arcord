"""
Date created (dd/mm/yy): 06/11/26
Author: Roshan
License: MIT
"""

import socket
import json
import sys
import random
import string
import colorama
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5.0)
server_addr: tuple[str, int] = ("127.0.0.1", 8653)

username = f"{"".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=10))}{random.randint(0, 9999):04d}"
print(f"{colorama.Fore.LIGHTBLUE_EX}{username}{colorama.Fore.RESET}")


def send_packet(data: dict) -> int:
    return sock.sendto(json.dumps(data).encode("utf-8"), server_addr)


class App(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Arcord")
        self.resize(960, 480)
        self.messages_ = QScrollArea(self)
        self.messages_.setStyleSheet(
            "QScrollArea {" "   border: 2px solid white;" "   border-radius: 10px;" "}"
        )
        self.messages_.setGeometry(0, 0, 760, 430)
        self.messages_.setWidgetResizable(True)
        self.messages = QLabel(self)
        self.messages.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_.setWidget(self.messages)
        self.old_messages = []

        self.users_online_ = QScrollArea(self)
        self.users_online_.setStyleSheet(
            "QScrollArea {" "   border: 2px solid white;" "   border-radius: 10px;" "}"
        )
        self.users_online_.setGeometry(760, 0, 200, 430)
        self.users_online_.setWidgetResizable(True)
        self.users_online = QLabel(self)
        self.users_online.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.users_online.setStyleSheet(
            "QLabel {"
            "   font-size: 15px;"
            "   font-weight: bold;"
            "   padding: 4px 8px;"
            "}"
        )
        self.users_online_.setWidget(self.users_online)
        self.old_users_online = []

        self.message_entry = QLineEdit(self)
        self.message_entry.setPlaceholderText(
            "Enter a message..."
        )  # interesting never knew this method existed
        self.message_entry.setGeometry(0, 430, 780, 50)
        self.message_entry.editingFinished.connect(self.send_message)

        self.message_button = QPushButton("Send messsage", self)
        self.message_button.setStyleSheet(
            "QPushButton {"
            "   background-color: rgb(75, 0, 255);"
            "   border: 2px solid white;"
            "   border-radius: 10px;"
            "}"
            "QPushButton:hover {"
            "   background-color: rgb(50, 0, 255);"
            "}"
        )
        self.message_button.clicked.connect(self.send_message)
        self.message_button.setGeometry(780, 430, 180, 50)

        self.mainloop_loop = QTimer(self)
        self.mainloop_loop.timeout.connect(self.mainloop)
        self.mainloop_loop.start(120)
        send_packet({"type": "con", "username": username})

    def mainloop(self) -> None:
        self.get_messages()
        self.get_online_users()

    def send_message(self) -> None:
        send_packet(
            {
                "type": "POST",
                "username": username,
                "message": self.message_entry.text(),
                "request": "message",
            }
        )  # I think this is how i do it
        self.message_entry.setText("")

    def get_messages(self) -> None:
        try:
            send_packet({"type": "GET", "request": "messages"})
            data, _ = sock.recvfrom(65536)
            messages = json.loads(data)
        except ConnectionResetError:
            self.deleteLater()
            return
        if messages != self.old_messages:
            text = ""
            for user, message in messages:
                text += f"{user}: {message}\n"

            self.messages.setText(text)
            self.old_messages = [message.copy() for message in messages]

    def get_online_users(self) -> None:
        try:
            send_packet({"type": "GET", "request": "online_users"})
            data, _ = sock.recvfrom(65536)
            online_users = json.loads(data)
        except ConnectionResetError:
            self.deleteLater()
            return

        if self.old_users_online != online_users:
            text = ""
            for user in online_users:
                text += f"{user}\n"

            self.users_online.setText(text)
            self.old_users_online = [online_user for online_user in online_users]

    def closeEvent(self, event: QCloseEvent) -> None:
        send_packet({"type": "dis", "username": username})
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    win = App()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
