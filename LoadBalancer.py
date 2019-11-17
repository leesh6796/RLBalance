import socket
import select
import time
import sys
import random

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
delay = 0.0001
server_list = [('127.0.0.1', 10500)]#, ('127.0.0.1', 10501)]


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


class MainServer:
	def __init__(self, host, port):
		self.socket_list = [] # 서버에서 관리하는 소켓들 저장. 첫 번째 소켓은 서버 소켓
		self.channel = {}

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

				self.data = self.s.recv(buffer_size)
				if len(self.data) == 0:
					self.on_close()
					break
				else:
					self.on_recv()


	def on_accept(self):
		load = RandomLoadBalancer()
		destIp, destPort = load.getForward()

		forward = Forward().start(destIp, destPort)
		clientsock, clientaddr = self.server.accept()
		if forward:
			print(clientaddr, "has connected")
			self.socket_list.append(clientsock)
			self.socket_list.append(forward)
			self.channel[clientsock] = forward
			self.channel[forward] = clientsock
		else:
			print("Can't establish connection with remote server.")
			print("Closing connection with client side", clientaddr)
			clientsock.close()


	def on_close(self):
		print(self.s.getpeername(), "has disconnected")
		#remove objects from socket_list
		self.socket_list.remove(self.s)
		self.socket_list.remove(self.channel[self.s])
		out = self.channel[self.s]
		# close the connection with client
		self.channel[out].close()  # equivalent to do self.s.close()
		# close the connection with remote server
		self.channel[self.s].close()
		# delete both objects from channel dict
		del self.channel[out]
		del self.channel[self.s]


	def on_recv(self):
		data = self.data
		# here we can parse and/or modify the data before send forward
		#print(data)
		self.channel[self.s].send(data)


if __name__ == '__main__':
	server = MainServer('', 9090)
	try:
		print("Start LoadBalancer")
		server.main_loop()
	except KeyboardInterrupt:
		print("Ctrl C - Stopping server")
		sys.exit(1)