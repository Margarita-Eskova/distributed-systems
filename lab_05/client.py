import socket
import threading

class ChatClient:
    def __init__(self, host='127.0.0.1', port=9090):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                if message == "NICK":
                    self.client.send(self.nickname.encode())
                else:
                    print(message)
            except:
                print("Отключён от сервера")
                self.client.close()
                break

    def write_messages(self):
        while True:
            message = f"{self.nickname}: {input()}"
            self.client.send(message.encode())

    def run(self):
        self.client.connect((self.host, self.port))
        self.nickname = input("Введите ваш никнейм: ")

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write_messages)
        write_thread.start()

if __name__ == "__main__":
    client = ChatClient()
    client.run()
