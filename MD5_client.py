import hashlib
import socket
import multiprocessing
import protocol


class Client:
    def __init__(self):
        self.IP = "127.0.0.1"
        print(self.IP)
        self.SERVER_PORT = 8080
        self.SERVER_ADDR = (self.IP, self.SERVER_PORT)
        self.client_socket = socket.socket()
        self.md5_word = None
        self.start_try = None
        self.end_try = None
        self.segments = []
        self.processes = []
        self.segment = int(multiprocessing.cpu_count() * 0.8)

    def start(self):
        self.connect_to_server(self.IP)
        self.set_proc()
        data = protocol.recv_data(self.client_socket).decode()
        while data != "stop":
            data = protocol.recv_data(self.client_socket).decode()
            if "new segment is:" in data:
                self.kill_proc()
                self.start_try = int(data.split("|")[1])
                self.end_try = int(data.split("|")[2])
                print(f"The MD5 hash word is: {self.md5_word}\r\n start: {self.start_try}\r\n end: {self.end_try}")
                self.set_proc()

        self.kill_proc()

    def set_proc(self):
        _processes = []
        self.processes = []
        self.set_segments()
        for i in range(self.segment):
            proc = multiprocessing.Process(target=self.handle_data, args=(int(self.segments[i][0]),
                                                                          int(self.segments[i][1])), daemon=True)
            _processes.append(proc)
            proc.start()
        self.processes = _processes

    def kill_proc(self):
        for proc in self.processes:
            proc.kill()

    def set_segments(self):
        self.segments = []
        num_range = (self.end_try - self.start_try) // self.segment
        start = self.start_try
        for i in range(self.segment):
            end = start + num_range if i != self.segment - 1 else self.end_try
            self.segments.append((start, end))
            start = end
        for i, seg in enumerate(self.segments):
            print(f"process {i + 1}: {seg}")
        print("------------------------------------")

    def connect_to_server(self, addr="127.0.0.1"):
        self.client_socket.connect((addr, self.SERVER_PORT))
        protocol.send_data(self.client_socket, "worker".encode())
        self.md5_word, self.start_try, self.end_try = protocol.recv_data(self.client_socket).decode().split("|")
        self.start_try, self.end_try = int(self.start_try), int(self.end_try)
        print(f"The MD5 hash word is: {self.md5_word}\r\nstart: {self.start_try}\r\nend: {self.end_try}")

    def handle_data(self, start, end):
        try:
            current_try = start
            counter = 0
            while current_try <= end:
                result = hashlib.md5(str(current_try).encode()).hexdigest()
                if counter % 50000 == 0:
                    protocol.send_data(self.client_socket, "50000".encode())
                if result.lower() == self.md5_word.lower():
                    protocol.send_data(self.client_socket, str(f"The MD5 number is: {current_try}").encode())
                    print(f"Done! The number is {current_try}")

                current_try += 1
                counter += 1
            protocol.send_data(self.client_socket, f"new |{self.start_try}|{self.end_try}".encode())

        except Exception:  # closing connection
            self.client_socket.close()
            print('Connection closed')


if __name__ == '__main__':
    c = Client()
    c.start()