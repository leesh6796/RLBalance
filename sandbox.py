bufSize = 4096
f = open("filewriter.py", "rb")
data = f.read(bufSize)
print(data)
print(len(data))