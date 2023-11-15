#ifndef COMM_SYSTEM
#define COMM_SYSTEM
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string.h>

#define SERVER_PORT 65431
#define SERVER_IP "127.0.0.1"

void *comm_system(void*);

#endif
