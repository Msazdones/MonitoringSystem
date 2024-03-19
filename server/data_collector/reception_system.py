import config as cfg

def connect_to_db():
	client = cfg.MongoClient(cfg.MONGO_DIR)
	return client[cfg.DB_CREDS][cfg.credsCOLL]

def check_login(col, passphrase):
	dbhpassphrase = col.find_one({},{"_id": 0, "passwd": 1})["passwd"] 

	hpassphrase = cfg.sha256(passphrase.encode("utf-8")).hexdigest()

	if(hpassphrase == dbhpassphrase):
		return True

	return False

def initial_setup(q, conn):
	data = conn.recv(cfg.MAX_BLIND_DATA)
	if not data:
		print("Something went wrong. Aborting.")
	q.append(data.decode(cfg.DECODING))
	conn.sendall(cfg.ACK_MSG)

	print(data.decode(cfg.DECODING))

def reception():
	col = connect_to_db()
	# Crea un socket TCP
	ssocket = cfg.socket.socket(cfg.socket.AF_INET, cfg.socket.SOCK_STREAM)

	# Escucha conexiones entrantes en el puerto 65432
	ssocket.bind((cfg.HOST, cfg.PORT))
	ssocket.listen(cfg.MAX_CLIENTS)

	# Crea un contexto TLS
	context = cfg.ssl.SSLContext(cfg.ssl.PROTOCOL_TLS_SERVER)
	context.load_cert_chain(certfile="./keys/rootCA.pem", keyfile="./keys/rootCA.key")
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
			
			client_socket.sendall(cfg.PASS_REQ)
			print("Passphrase requested.")

		for client in client_list:
			try:
				if client in rs:
					cmsg = client.recv(cfg.MAX_BLIND_DATA).decode(cfg.DECODING)
					if(cmsg[0:len(cfg.PASS_RES)] == cfg.PASS_RES):
						if(not check_login(col, cmsg[len(cfg.PASS_RES):len(cmsg)])):
							client.sendall(cfg.NACK_MSG)
							print("Wrong passphrase. Exiting.")
							raise ValueError("Wrong passphrase. Exiting.")
						
						print("Client authenticated.")
						print("Starting data collection process for client", client.getpeername())
						client.sendall(cfg.ACK_MSG)
						initial_setup(shared_lists[client_list.index(client)], client)
					
					elif(cmsg[0:len(cfg.DATA_SIZE)] == cfg.DATA_SIZE):
						data_size = int(cmsg[len(cfg.DATA_SIZE): len(cmsg)])
						client.sendall(cfg.ACK_MSG)

						data = b''
						while(len(data) < data_size):
							data += client.recv(data_size)

						if not data:
							client.close()
							del shared_lists[client_list.index(client)]
							client_list.remove(client)
							continue
						
						shared_lists[client_list.index(client)].append(data.decode(cfg.DECODING))
			except Exception as error:
				cindex = client_list.index(client)

				prs[cindex].terminate()
				del prs[cindex]

				client.close()
				del shared_lists[cindex]
				client_list.remove(client)
