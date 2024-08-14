#include "../headers/probe_body.h"
#include "../headers/server_comm.h"

int main(int argc, char **argv)
{
	int socket_desc;
	char label[20];

	if(argc > 2)
	{
		printf("Wrong number of input arguments. Exiting.\n")
		return -1;
	}
	else if(argc == 2)
	{
		strncpy(label, argv[1], sizeof(label));
	}
	else
	{
		strncpy(label, "", sizeof(label));
	}
	
	SSL_CTX *ctx = SSL_CTX_new(TLS_method());

	if (SSL_CTX_load_verify_locations(ctx, SERVER_CERT, NULL) != 1) {
		printf("Loading cert failure. Exiting.\n");
		return -1;
	}

	SSL *sslsock = SSL_new(ctx);

	if(!create_connection(&socket_desc))
	{
		close_connections(&sslsock, &socket_desc);
		SSL_free(sslsock);
		return -1;
	}

	if(!create_secure_connection(&sslsock, &socket_desc))
	{
		close_connections(&sslsock, &socket_desc);
		SSL_free(sslsock);
		return -1;
	}

	if(!introduce_creds(&sslsock))
	{
		close_connections(&sslsock, &socket_desc);
		SSL_free(sslsock);
		return -1;
	}

	if(!initial_setup(&sslsock, label))
	{
		close_connections(&sslsock, &socket_desc);
		SSL_free(sslsock);
		return -1;
	}

	return probe_body(&sslsock);
}