import config as cfg

def initial_setup(q, conn):
	data = conn.recv(cfg.MAX_BLIND_DATA)
	if not data:
		print("Something went wrong. Aborting\n")
	q.append(data.decode(cfg.DECODING))

	conn.sendall(cfg.ACK_MSG)

def reception():
	prs = []
	manager = cfg.mp.Manager()
	shared_lists = []

	ssocket= cfg.socket.socket(cfg.socket.AF_INET, cfg.socket.SOCK_STREAM)
	ssocket.bind((cfg.HOST, cfg.PORT))
	ssocket.listen(cfg.MAX_CLIENTS)
	print("Data recption system active. Waiting for the connection.\n")
	
	client_list = [ssocket]
	while True:
		rs, ws, es = cfg.select.select(client_list, [], [])
		for i in range(0, len(rs)):
			if rs[i] is ssocket:
				client_socket, addr = ssocket.accept()
				client_list.append(client_socket)

				shared_lists.append(manager.list())
				last_sl = len(shared_lists) - 1

				p = cfg.mp.Process(target=cfg.dms.data_management, args=(shared_lists[last_sl], addr[0]))
				prs.append(p)
				p.start()

				initial_setup(shared_lists[last_sl], client_socket)

				print(f"Connected by {addr}")
			else:
				data_size = rs[i].recv(cfg.MAX_BLIND_DATA)
				rs[i].sendall(cfg.ACK_MSG)

				data = rs[i].recv(int(data_size.decode(cfg.DECODING)), cfg.socket.MSG_WAITALL)
				if data:
					shared_lists[i-1].append(data.decode(cfg.DECODING))
				else:
					rs[i].close()
					client_list.remove(rs[i])
					shared_lists.remove(shared_lists[i-1])

	"""conn, addr = s.accept()

	print(f"Connected by {addr}")
	initial_setup(shared_queue, conn)
	while True:
		data_size = conn.recv(cfg.MAX_BLIND_DATA)
		conn.sendall(cfg.ACK_MSG)

		data = conn.recv(int(data_size.decode(cfg.DECODING)), cfg.socket.MSG_WAITALL)
		if not data:
			break
		shared_queue.append(data.decode(cfg.DECODING))
		#print(shared_queue)"""
