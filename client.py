import customtkinter as ctk
import socket
import json
import random

server_address: tuple[str, int] = ("127.0.0.1", 4000)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5.0)

username: str = f"test{random.randint(0, 9999)}"
messages = None


class Window(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arcord Client App")
        self.geometry("960x480")
        self.messages_frame = ctk.CTkScrollableFrame(self)
        self.messages_frame.pack(side="top", fill="both", expand=True)
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(side="top", fill="x")
        self.message_entry = ctk.CTkEntry(
            self.input_frame, placeholder_text="Enter a message"
        )
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self.input_frame, text="SEND", command=self.send_message).pack(
            side="left"
        )

        self.after(150, self.get_messages)

    def send_message(self, event=None):
        global username
        template = {"username": username, "message": self.message_entry.get()}

        sock.sendto(json.dumps(template).encode(), server_address)

    def get_messages(self):
        global messages
        if messages:
            old_messages = messages
        else:
            old_messages = None
        try:
            sock.sendto(b"GET_MESSAGES", server_address)
        except (OSError, TimeoutError, ConnectionRefusedError):
            return

        data, _ = sock.recvfrom(4096)
        messages = json.loads(data)

        if old_messages != messages:
            for message_label in self.messages_frame.winfo_children():
                message_label.destroy()

            for user, message in messages:
                ctk.CTkLabel(self.messages_frame, text=f"{user}: {message}").pack(
                    side="top"
                )

        self.after(100, self.get_messages)


if __name__ == "__main__":
    root = Window()
    root.mainloop()
