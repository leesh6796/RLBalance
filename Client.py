import socket
import time
import sys
import random
from multiprocessing import *

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
		self.requestSize = self.size[i]
		print("Request " + self.requestSize)
		self.socket.send(self.requestSize.encode())


	def recvVideoResponse(self):
		#recvFile = open("recvFile.mp4", "wb")
		startTime = time.time()

		length = self.socket.recv(bufSize).decode()
		remain = int(length[:length.index('e')]) - (len(length) - length.index('e') + 1)
		while remain > 0:
			buf = self.socket.recv(bufSize)
			remain -= len(buf)

		endTime = time.time()

		interval = str(endTime - startTime)
		print("Success " + self.requestSize + " " + interval) # seconds

		self.socket.send(("t" + interval).encode())

		self.socket.close()



def Simulation1_handle(host, port, wait):
	client = MainClient()
	print(host, port, '로 연결')
	client.connect(host, port)
	client.sendVideoRequest()
	client.recvVideoResponse()


def Simulation1():
	try:
		num_clients = 10
		host, port = '127.0.0.1', 9090

		processList = []

		for i in range(num_clients):
			process = Process(target=Simulation1_handle, args=(host, port, 0))
			process.daemon = True
			process.start()
			processList.append(process)

		for i in range(num_clients):
			processList[i].join()

	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")

	finally:
		for process in active_children():
			process.terminate()
			process.join()

		print("Close server")
		sys.exit(1)


if __name__ == '__main__':
	#try:
	Simulation1()

	#except KeyboardInterrupt:
	#	print("Ctrl C - Stopping server")
	#	sys.exit(1)