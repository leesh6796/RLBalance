import socket
import select
import time
import sys
import os

bufSize = 4096
delay = 0.0001


class MainServer:
	def __init__(self, host, port):
		self.socket_list = [] # 서버에서 관리하는 소켓들 저장. 첫 번째 소켓은 서버 소켓

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((host, port))
		self.server.listen(200)


	def main_loop(self):
		self.socket_list.append(self.server)
		while True:
			time.sleep(delay)
			ss = select.select
			inputready, outputready, exceptready = ss(self.socket_list, [], [])
			for self.s in inputready:
				if self.s == self.server:
					self.on_accept()
					break

				self.data = self.s.recv(bufSize)
				if len(self.data) == 0:
					self.on_close()
					break
				else:
					self.on_recv()


	def on_accept(self):
		clientsock, clientaddr = self.server.accept()
		print(clientaddr, "has connected")
		self.socket_list.append(clientsock)


	def on_close(self):
		print(self.s.getpeername(), "has disconnected")
		#remove objects from socket_list
		self.socket_list.remove(self.s)


	def on_recv(self):
		data = self.data
		# here we can parse and/or modify the data before send forward
		requestSize = data.decode()
		videoFileName = "video" + str(requestSize) + ".mp4"
		videoFileLength = os.path.getsize(videoFileName) # bytes
		videoFile = open(videoFileName, "rb")

		# 맨 처음에 video file length를 size + e로 보낸다.
		remain = videoFileLength
		self.s.send((str(remain) + "e").encode())
		while remain > 0:
			buf = videoFile.read(bufSize)
			self.s.send(buf)
			remain -= bufSize
			print("remain: " + str(remain))


if __name__ == '__main__':
	port = int(sys.argv[1])
	server = MainServer('', port)
	try:
		print("Start Server")
		server.main_loop()
	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")
		sys.exit(1)