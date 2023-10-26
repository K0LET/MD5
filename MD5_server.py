import socket
import threading
import traceback
import protocol


class Server:
    def __init__(self, word):
        self.server_ip = "0.0.0.0"
        self.server_port = 8080
        self.server_addr = (self.server_ip, self.server_port)

        self.server_socket = socket.socket()
        self.server_socket.bind(self.server_addr)
        self.server_socket.listen()
        print("server is up and running")
        self.clients = []
        self.gui_client = None  # type: socket.socket
        self.threads = []
        self.md5_word = word
        self.segments = []  # ((start, end), occupied, finished)
        self.tries = 0
        self.run = True

    def handle_client(self, client_socket: socket.socket, client_address):
        while self.run:
            try:
                data = protocol.recv_data(client_socket).decode()
                if data != "":
                    if data == "50000":
                        self.tries += 50000
                        protocol.send_data(self.gui_client, "add".encode())
                    elif "The MD5 number is:" in data:
                        print(data)
                        self.run = False
                        protocol.send_data(self.gui_client, data.encode())
                        for c in self.clients:
                            protocol.send_data(c[0], "stop".encode())
                        break
                    elif "new" in data:
                        start, end = data.split("|")[1:]
                        start, end = int(start), int(end)
                        if not any([b[1] for b in self.segments]):
                            protocol.send_data(client_socket, "stop".encode())
                            continue
                        for i, seg in enumerate(self.segments):
                            if seg[1]:
                                self.segments[i] = (self.segments[i][0], False, False)
                                protocol.send_data(client_socket, f"new segment is: |{seg[0][0]}|{seg[0][1]}".encode())
                                break
                            if seg[0] == (start, end):
                                self.segments[i] = (self.segments[i][0], False, True)

            except Exception as e:
                traceback.print_exception(e)
                print(f'Client {client_address} disconnected')
                for c in self.clients:
                    if c[0] == client_socket:
                        start, end = c[1]
                        for i in range(len(self.segments)):
                            if self.segments[i][0] == (start, end):
                                self.segments[i] = (self.segments[i][0], True, False)
                                print(f"{self.segments[i][0]} is free")
                                break
                        break

                break

    def accept_connection(self):
        client_socket, client_address = self.server_socket.accept()
        data = protocol.recv_data(client_socket).decode()
        if data == "gui":
            print(f'The GUI client address {client_address}')
            self.gui_client = client_socket
            return
        if data == "worker" and self.gui_client is None:
            print("the gui client is not connected yet")
            client_socket.close()
            return
        start, end = 0, 0
        for i in range(len(self.segments)):
            if self.check_if_free(self.segments[i][0]):
                protocol.send_data(client_socket, (self.md5_word + b"|" + str(self.segments[i][0][0]).encode() + b"|"
                                   + str(self.segments[i][0][1]).encode()))  # start package
                self.segments[i] = (self.segments[i][0], False, False)
                start, end = self.segments[i][0]
                break
        self.clients.append((client_socket, (start, end)))
        print(f'Accepted new connection from {client_address}')
        client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True)
        self.threads.append(client_thread)
        client_thread.start()

    def check_if_free(self, start_end):
        for seg in self.segments:
            if seg[0] == start_end:
                return seg[1]

    def set_segments(self):
        segment = 21
        num_range = ((10 ** 10) - (10**9)) // segment
        for i in range(segment):
            start = num_range * i + (10**9)
            end = start + num_range if i != segment - 1 else 10 ** 10
            self.segments.append(((start, end), True, False))

    def start(self):
        self.set_segments()
        for i in range(len(self.segments)):
            self.accept_connection()


if __name__ == '__main__':
    md5 = input("what is the MD5 number?")
    s = Server(md5.encode())  # EC9C0F7EDCC18A98B1F31853B1813301
    s.start()
