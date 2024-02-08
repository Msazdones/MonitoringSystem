#ifndef PROBE_BODY
#define PROBE_BODY

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/sysinfo.h>
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <ctype.h>
#include <unistd.h> 

#define BUFFER_SIZE 1000
#define MAX_PROCS_TO_EVAL 1000

//mensajes de protocolo de comunicaciones
#define ACK_MSG "OK"
#define NACK_MSG "NOK"
#define PASS_REQ "PASS"
#define PASS_RES "AUTH"
#define DATA_SIZE "SIZE"

int initial_setup(SSL **);
int probe_body(SSL **);
int introduce_creds(SSL **);

#endif