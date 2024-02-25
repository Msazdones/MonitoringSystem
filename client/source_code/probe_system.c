#include "../headers/probe_body.h"
#include "../headers/server_comm.h"

int main()
{
	int socket_desc;
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

	if(!initial_setup(&sslsock))
	{
		close_connections(&sslsock, &socket_desc);
		SSL_free(sslsock);
		return -1;
	}

	return probe_body(&sslsock);
}