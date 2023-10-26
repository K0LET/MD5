import socket
from builtins import ConnectionError


def send_data(sock: socket.socket, data: bytes) -> bool:
    try:
        sock.sendall(f"{len(data)}".ljust(30).encode() + data)
    except (ConnectionError, OSError):
        return False
    return True


def recvall(sock: socket.socket, buffsize: int) -> bytes:
    data = b""
    while len(data) < buffsize:
        res = sock.recv(buffsize - len(data))
        data += res
        if res == b"":  # connection closed
            raise ConnectionError
    return data


def recv_data(sock: socket.socket):
    data_length = recvall(sock, 30).decode()
    if data_length != '':
        return recvall(sock, buffsize=int(data_length.strip()))
