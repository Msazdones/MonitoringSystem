#ifndef DATA_GATHERING
#define DATA_GATHERING

#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <sys/sysinfo.h>
#include <stdlib.h>
#include <unistd.h>

#define PROC_DIR "/proc/"
#define MAX_PROCS_TO_EVAL 1000
#define BUFFER_SIZE 2500
#define FILES_TO_EVAL 4

void data_gathering(char **);
int isNameNumber(char *);

#endif