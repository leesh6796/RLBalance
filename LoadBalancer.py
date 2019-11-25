import socket
from multiprocessing import *
import time
import sys
import random

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
bufSize = 4096
delay = 0.0001
offset = 10000
num_servers = 5
server_list = [('127.0.0.1', 10500+x) for x in range(num_servers)]


class RandomLoadBalancer():
	def __init__(self):
		pass


	def getForward(self): # () => (ip: str, port: int)
		i = random.randrange(0,len(server_list))
		return server_list[i]


class RoundRobinLoadBalancer():
	def __init__(self):
		self.i = 0
		self.maxIdx = len(server_list)


	def getForward(self): # () => (ip: str, port: int)
		if self.i == self.maxIdx:
			self.i = 0
		forward = server_list[i]
		self.i += 1
		return forward


class Forward:
	def __init__(self):
		self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def start(self, host, port):
		try:
			self.forward.connect((host, port))
			return self.forward
		except Exception as e:
			print(e)
			return False


def ProxyHandle(srcSock, srcAddr, destSock, destAddr, tag, rewards):
	# tag=0 -> client -> server
	# tag=1 -> server -> client
	while True:
		data = srcSock.recv(bufSize)

		if len(data) == 0:
			break

		if tag == 0 and data.decode()[0] == "t": # If clients
			rewards.append(data.decode()[1:])
			print(rewards[-1])

		destSock.send(data)

	#srcSock.close() # destSock은 반대쪽 process에서 해제할 것


def HealthCheckHandle(conn, index, serverStates):
	while True:
		data = conn.recv(bufSize)
		if len(data) > 0:
			tmp = data.decode().split("$")
			num_clients, remainVideo = int(tmp[0]), int(tmp[1])
			serverStates[2 * index] = num_clients
			serverStates[2 * index + 1] = remainVideo


class MainServer:
	def __init__(self, host, port):
		self.socket_list = [] # 서버에서 관리하는 소켓들 저장. 첫 번째 소켓은 서버 소켓
		self.healthCheckSocketList = []
		self.channel = {}

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((host, port))
		self.server.listen(2000)

		self.serverStates = Array('i', [0 for i in range(num_servers * 2)])
		self.rewards = Array('d', [])


	def healthCheckStart(self):
		for i in range(5):
			sock_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock_check.connect((server_list[i][0], server_list[i][1] + offset))
			self.healthCheckSocketList.append(sock_check)

			p = Process(target=HealthCheckHandle, args=(sock_check, i, self.serverStates))
			p.daemon = True
			p.start()


	def main_loop(self):
		self.socket_list.append(self.server)
		while True:
			srcSock, srcAddr = self.server.accept()
			#load = RandomLoadBalancer()
			load = RoundRobinLoadBalancer()
			destIp, destPort = load.getForward()
			destAddr = (destIp, destPort)
			destSock = Forward().start(destIp, destPort)

			p1 = Process(target=ProxyHandle, args=(srcSock, srcAddr, destSock, destAddr, 0, self.rewards))
			p2 = Process(target=ProxyHandle, args=(destSock, destAddr, srcSock, srcAddr, 1, None))
			p1.daemon = True
			p2.daemon = True
			p1.start()
			p2.start()


if __name__ == '__main__':
	server = MainServer('', 9090)
	try:
		print("Start LoadBalancer")
		server.healthCheckStart()
		server.main_loop()
	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")
	except Exception as e:
		print(e)
	finally:
		server.server.close()
		for process in active_children():
			process.terminate()
			process.join()
		print("Close server")
		sys.exit(1)