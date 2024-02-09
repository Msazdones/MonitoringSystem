#ifndef SERVER_COMM
#define SERVER_COMM

#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

#define SERVER_PORT 65432
#define SERVER_IP "192.168.50.152"

int create_connection(int *);
int create_secure_connection(SSL **, int *);
void close_connections(SSL **, int *);

#endif
