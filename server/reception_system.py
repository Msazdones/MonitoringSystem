import dependencies as dep
import config as cfg

def initial_setup(q, conn):
	data = conn.recv(cfg.MAX_BLIND_DATA)
	if not data:
		print("Something went wrong. Aborting\n")
	q.append(data.decode(cfg.DECODING))
	conn.sendall(cfg.ACK_MSG)

def reception(q):
	with dep.socket.socket(dep.socket.AF_INET, dep.socket.SOCK_STREAM) as s:
		s.bind((cfg.HOST, cfg.PORT))
		s.listen()
		print("Data recption system active. Waiting for the connection.\n")
		conn, addr = s.accept()
		with conn:
			print(f"Connected by {addr}")
			initial_setup(q, conn)
			while True:
				data_size = conn.recv(cfg.MAX_BLIND_DATA)
				conn.sendall(cfg.ACK_MSG)

				data = conn.recv(int(data_size.decode(cfg.DECODING)), dep.socket.MSG_WAITALL)
				if not data:
					break
				q.append(data.decode(cfg.DECODING))
