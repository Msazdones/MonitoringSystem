import config as cfg

def initial_setup(q, conn):
	data = conn.recv(cfg.MAX_BLIND_DATA)
	if not data:
		print("Something went wrong. Aborting\n")
	q.append(data.decode(cfg.DECODING))
	conn.sendall(cfg.ACK_MSG)

def reception():
	# Crea un socket TCP
	ssocket = cfg.socket.socket(cfg.socket.AF_INET, cfg.socket.SOCK_STREAM)

	# Escucha conexiones entrantes en el puerto 65432
	ssocket.bind((cfg.HOST, cfg.PORT))
	ssocket.listen(5)

	# Crea un contexto TLS
	context = cfg.ssl.SSLContext(cfg.ssl.PROTOCOL_TLS_SERVER)

	# Envuelve el socket en un socket TLS
	ssl_ssocket = context.wrap_socket(ssocket, server_side=True)

	prs = []
	manager = cfg.mp.Manager()
	shared_lists = []

	print("Data recption system active. Waiting for the connection.\n")
	
	client_list = []
	while True:
		rs, ws, es = cfg.select.select([ssl_ssocket] + client_list, [], client_list)
		
		if ssl_ssocket in rs:
			client_socket, addr = ssl_ssocket.accept()
			client_list.append(client_socket)

			shared_lists.append(manager.list())
			last_sl = len(shared_lists) - 1

			p = cfg.mp.Process(target=cfg.dms.data_management, args=(shared_lists[last_sl], addr[0]))
			prs.append(p)
			p.start()

			print(f"Connected by {addr}")
			initial_setup(shared_lists[last_sl], client_socket)

		for client in client_list:
			if client in rs:
				data_size = client.recv(cfg.MAX_BLIND_DATA)
				data_size = int(data_size.decode(cfg.DECODING))
				client.sendall(cfg.ACK_MSG)

				data = b''
				while(len(data) < data_size):
					data += client.recv(data_size)

				if not data:
					client.close()
					del shared_lists[client_list.index(client)]
					client_list.remove(client)
					continue
				
				print(client.getpeername())
				shared_lists[client_list.index(client)].append(data.decode(cfg.DECODING))
