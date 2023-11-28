import socket

def initial_setup(q, conn):
	data = conn.recv(1000000000)
	if not data:
		print("Something went wrong. Aborting\n")
	q.append(data.decode("latin-1"))
	conn.sendall(b"OK")

def reception(q):
	HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
	PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, PORT))
		s.listen()
		print("Data recption system active. Waiting for the connection.\n")
		conn, addr = s.accept()
		with conn:
			print(f"Connected by {addr}")
			initial_setup(q, conn)
			while True:
				data_size = conn.recv(1000000000)
				conn.sendall(b"OK")

				data = conn.recv(int(data_size.decode("latin-1")), socket.MSG_WAITALL)
				if not data:
					break
				q.append(data.decode("latin-1"))
				#print(data.decode("latin-1"))
				#conn.sendall(data)
