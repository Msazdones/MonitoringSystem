#ifndef PROBE_BODY
#define PROBE_BODY

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/sysinfo.h>
#include <ctype.h>
#include <unistd.h> 

#define BUFFER_SIZE 1000
#define MAX_PROCS_TO_EVAL 1000

//mensajes de protocolo de comunicaciones
#define ACK_MSG "OK"

int initial_setup(int *);
int probe_body(int *);

#endif