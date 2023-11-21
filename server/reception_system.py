import socket

def reception(q):
	HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
	PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, PORT))
		s.listen()
		conn, addr = s.accept()
		with conn:
			print(f"Connected by {addr}")
			while True:
				data = conn.recv(1000000)
				if not data:
					break
				q.append(data.decode("latin-1"))
				#print(data.decode("latin-1"))
				#conn.sendall(data)
