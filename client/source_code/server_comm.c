#include "../headers/server_comm.h"


int create_connection(int *sockfd)
{
	struct sockaddr_in addr;
	int connect_result;

	// Crea un socket TCP
	*sockfd = socket(AF_INET, SOCK_STREAM, 0);

	if (*sockfd < 0) {
		printf("Fallo en la creación del socket\n");
		return 0;
	}

	// Conecta el socket al servidor
	addr.sin_family = AF_INET;
	addr.sin_port = htons(SERVER_PORT);
	addr.sin_addr.s_addr = inet_addr(SERVER_IP);

	connect_result = connect(*sockfd, (struct sockaddr *)&addr, sizeof(addr));
	if (connect_result < 0) 
	{
		printf("Fallo en el establecimiento de la comunicación\n");
		return 0;
	}

	return 1;
}

int create_secure_connection(SSL **ssl, int *sockfd)
{
	// Crea un socket TLS
	if(SSL_set_fd(*ssl, *sockfd) < 0)
	{
		return 0;
	}
	
	if(SSL_set_tlsext_host_name(*ssl, SERVER_IP) < 0)
	{
		return 0;
	}

	if(SSL_connect(*ssl) < 0)
	{
		return 0;
	}

	return 1;
}

void close_connections(SSL **ssl, int *sockfd)
{
	// Cierra la conexión
	SSL_shutdown(*ssl);
	shutdown(*sockfd, SHUT_RDWR);
}