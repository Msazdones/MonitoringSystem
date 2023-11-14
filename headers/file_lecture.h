#ifndef FILE_LECTURE
#define FILE_LECTURE

#include <stdio.h>
#include <dirent.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <unistd.h> 
#include <sys/sysinfo.h>
#include <time.h>


//constantes
#define BUFFERSIZE 1000
#define DATAFILESCNT 3
#define UPFILE "/proc/uptime"
#define PROCDIR "/proc/"
#define MAXPATHSIZE  21
#define MAXNAMESIZE 10

#define MAXPROCS 1000
 
struct prrsd
{
	char prname[100];
	char pid[15];
	char status[2];
	char cpu[10];
	char ram[10];
	char rchar[10];
	char wchar[10];
};

extern int isNameNumber(char *);
extern void extractPrData(char[], struct prrsd**, int, double, double);

#endif
