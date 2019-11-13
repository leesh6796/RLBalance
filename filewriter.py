f = open("video1000.mp4", "w")
for i in range(1024 * 1024 * 1000):
	f.write("0")
f.close()