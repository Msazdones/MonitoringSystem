#include "../headers/probe_body.h"
#include "../headers/server_comm.h"

int main()
{
	int socket_desc;
	SSL_CTX *ctx = SSL_CTX_new(TLS_method());
	SSL *sslsock = SSL_new(ctx);

	if(!create_connection(&socket_desc))
	{
		return -1;
	}

	if(!create_secure_connection(&sslsock, &socket_desc))
	{
		return -1;
	}

	if(!initial_setup(&sslsock))
	{
		return -1;
	}

	return probe_body(&sslsock);
}