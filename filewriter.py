f = open("video1000.mp4", "wb")
for i in range(1000 * 1000 * 1000):
	f.write("0".encode())
f.close()