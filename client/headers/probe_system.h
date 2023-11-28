#ifndef PROBE_SYSTEM
#define PROBE_SYSTEM

#include <sys/socket.h>
#include <sys/sysinfo.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>
#include <dirent.h>
#include <stdlib.h>
#include <unistd.h> 

#define SERVER_PORT 65432
#define SERVER_IP "127.0.0.1"
#define PROC_DIR "/proc/"
#define UPFILE "/proc/uptime"
#define FILES_TO_EVAL 3
#define MAX_PROCS_TO_EVAL 1000
#define BUFFER_SIZE 1000
//mensajes de protocolo de comunicaciones
#define ACK_MSG "OK"

void gathering_data(char **);
int isNameNumber(char *);
int create_connection(int *, struct sockaddr_in *);
int initial_setup(int *);

#endif
