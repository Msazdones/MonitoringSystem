#ifndef SERVER_COMM
#define SERVER_COMM

#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>

#define SERVER_PORT 65432
#define SERVER_IP "127.0.0.1"

int create_connection(int *);

#endif