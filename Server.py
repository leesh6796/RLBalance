import socket
from multiprocessing import *
import time
import sys
import os

bufSize = 4096
delay = 0.0001
offset = 10000


def healthCheckHandle(conn, addr, num_clients, remainVideo):
	while True:
		d = str(num_clients.value) + "$" + str(remainVideo.value)
		conn.send(d.encode())
		#print(num_clients.value)
		#print(remainVideo.value)
		time.sleep(1) # 1 sec sleep


def videoSendHandle(conn, addr, num_clients, remainVideo):
	print(addr, "has connected")
	data = conn.recv(bufSize)

	requestSize = data.decode()
	videoFileName = "video" + str(requestSize) + ".mp4"
	videoFileLength = os.path.getsize(videoFileName) # bytes
	videoFile = open(videoFileName, "rb")

	# 맨 처음에 video file length를 size + e로 보낸다.
	remain = videoFileLength
	remainVideo.value += remain
	conn.send((str(remain) + "e").encode())
	while remain > 0:
		buf = videoFile.read(bufSize)
		conn.send(buf)
		sentBytes = len(buf)
		remain -= sentBytes
		remainVideo.value -= sentBytes

	num_clients.value -= 1
	print(str(addr) + " end of handle")


class MainServer:
	def __init__(self, host, port):
		self.socket_list = [] # 서버에서 관리하는 소켓들 저장. 첫 번째 소켓은 서버 소켓

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((host, port))
		self.server.listen(2000)

		self.sock_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock_check.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock_check.bind((host, port + offset))
		self.sock_check.listen(5)

		self.num_clients = Value('i', 0)
		self.remainVideo = Value('i', 0)


	def healthCheckStart(self):
		conn, addr = self.sock_check.accept()
		process = Process(target=healthCheckHandle, args=(conn, addr, self.num_clients, self.remainVideo))
		process.daemon = True
		process.start()


	def main_loop(self):
		self.socket_list.append(self.server)
		while True:
			conn, addr = self.server.accept()
			self.num_clients.value += 1
			process = Process(target=videoSendHandle, args=(conn, addr, self.num_clients, self.remainVideo))
			process.daemon = True
			process.start()


def ServerHandle(host, port):
	server = MainServer(host, port)
	print(str(port) + " Server start")
	server.healthCheckStart()
	server.main_loop()


if __name__ == '__main__':
	#port = int(sys.argv[1])
	port = 10500
	num_servers = 5

	try:
		print("Start Server")
		processList = []
		for i in range(num_servers):
			process = Process(target=ServerHandle, args=('', port + i))
			#process.daemon = True
			process.start()
			processList.append(process)

		for i in range(num_servers):
			processList[i].join()

	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")
	except Exception as e:
		print(e)
	finally:
		for process in active_children():
			process.terminate()
			process.join()

	print("Close server")
	sys.exit(1)