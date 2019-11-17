import socket
import time
import sys
import random

bufSize = 4096


class MainClient:
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.size = ["50", "200", "500", "1000"]


	def connect(self, host, port):
		try:
			self.socket.connect((host, port))
		except Exception as e:
			print(e)
			return False


	def sendVideoRequest(self):
		i = random.randrange(0, 1)
		self.socket.send(self.size[i].encode())


	def recvVideoResponse(self):
		#recvFile = open("recvFile.mp4", "wb")
		length = self.socket.recv(bufSize).decode()
		remain = int(length[:length.index('e')])
		print(remain)
		while remain > 0:
			buf = self.socket.recv(bufSize)
			remain -= bufSize
			#recvFile.write(buf)
		#recvFile.close()
		print("Success")


if __name__ == '__main__':
	client = MainClient()
	try:
		host, port = '127.0.0.1', 9090
		print(host, port, '로 연결')
		client.connect(host, port)
		client.sendVideoRequest()
		client.recvVideoResponse()

	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")
		sys.exit(1)