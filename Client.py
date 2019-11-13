import socket
import time
import sys


class MainClient:
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


	def connect(self, host, port):
		try:
			self.socket.connect((host, port))
		except Exception as e:
			print(e)
			return False


if __name__ == '__main__':
	client = MainClient()
	try:
		host, port = '127.0.0.1', 9090
		print(host, port, '로 연결')
		client.connect(host, port)
		client.socket.send("A".encode())

	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")
		sys.exit(1)