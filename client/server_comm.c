#include "headers/server_comm.h"

int create_connection(int *socket_desc)
{
	struct sockaddr_in server_addr;	
	*socket_desc = socket(AF_INET, SOCK_STREAM, 0);
	
	if(socket_desc < 0){
		printf("Fallo en la creación del socket\n");
		return 0;
	}
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(SERVER_PORT);
	server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

	if(connect(*socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
		printf("Fallo en el establecimiento de la comunicación\n");
		return 0;
	}
	printf("Conexión con el servidor central realizada con éxito\n");

	return 1;
}