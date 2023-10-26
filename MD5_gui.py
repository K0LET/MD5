import multiprocessing

import pygame
import threading
import sys
import socket
import protocol
import time


class Client:
    def __init__(self, progress_bar):
        self.IP = "127.0.0.1"
        print(self.IP)
        self.SERVER_PORT = 8080
        self.SERVER_ADDR = (self.IP, self.SERVER_PORT)
        self.client_socket = socket.socket()
        self.tries = 0
        self.progress_bar = progress_bar  # type: ProgressBar
        self.start_time = time.time()

    def connect_to_server(self, addr="127.0.0.1"):
        self.client_socket.connect((addr, self.SERVER_PORT))
        protocol.send_data(self.client_socket, "gui".encode())

    def handle_data(self):
        data = protocol.recv_data(self.client_socket).decode()
        while "The MD5 number is:" not in data:
            if data == "add":
                self.progress_bar.do_work()
            data = protocol.recv_data(self.client_socket).decode()

        self.progress_bar.set_text(data)
        self.progress_bar.text_rect = self.progress_bar.text.get_rect(center=(640, 360))
        print(f"Took {time.time() - self.start_time}")
        self.progress_bar.finished = True
        self.client_socket.close()
        print('Connection closed')

    def start_(self):
        self.connect_to_server()
        threading.Thread(target=self.handle_data, daemon=True).start()


class ProgressBar:
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Progress")
        self.font = pygame.font.SysFont("Roboto", 100)
        self.clock = pygame.time.Clock()
        self.work = 180000

        self.loading_bg = pygame.image.load("Loading.png")
        self.loading_bg_rect = self.loading_bg.get_rect(center=(640, 360))

        self.finished = False
        self.progress = 0
        self.percentage = 0

        self.text = self.font.render("Done!", True, "white")
        self.text_rect = self.text.get_rect(center=(640, 360))

    def do_work(self):
        self.progress += 1
        self.percentage = ((self.progress * 100) // self.work)

    def set_text(self, txt):
        self.text = self.font.render(txt, True, "white")

    def app_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill("#0d0e2e")

            if not self.finished:
                bar_width = int(self.percentage * 7.2)

                pygame.draw.rect(self.screen, (226, 65, 103), (270, 293, bar_width, 135))
                self.screen.blit(self.loading_bg, self.loading_bg_rect)

                self.screen.blit(self.font.render(f"{self.percentage}%", True, (226, 65, 103)), (620, 100))

            else:
                self.screen.blit(self.text, self.text_rect)

            pygame.display.update()
            self.clock.tick(30)


def main():
    pb = ProgressBar()
    c = Client(pb)
    c.start_()
    pb.app_loop()


if __name__ == '__main__':
    main()
