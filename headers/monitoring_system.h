#ifndef MONITORING_SYSTEM
#define MONITORING_SYSTEM

#include <sys/socket.h>
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
#define FILES_TO_EVAL 3
#define MAX_PROCS_TO_EVAL 1000
#define BUFFER_SIZE 1000

void gathering_data(char **);
int isNameNumber(char *);

#endif
