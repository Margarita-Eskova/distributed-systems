import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=9090):
        self.host = host
        self.port = port
        self.clients = []
        self.nicknames = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def broadcast(self, message, sender_conn=None):
        for client in self.clients:
            if client != sender_conn:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            idx = self.clients.index(client)
            self.clients.remove(client)
            client.close()
            nickname = self.nicknames.pop(idx)
            self.broadcast(f"{nickname} покинул чат\n".encode())

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    break
                self.broadcast(message, client)
            except:
                break
        self.remove_client(client)

    def receive_connections(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Сервер запущен на {self.host}:{self.port}")

        while True:
            client, address = self.server.accept()
            print(f"Подключён {address}")

            client.send("NICK".encode())
            nickname = client.recv(1024).decode()

            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f"Никнейм: {nickname}")
            self.broadcast(f"{nickname} присоединился к чату\n".encode())

            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.receive_connections()
