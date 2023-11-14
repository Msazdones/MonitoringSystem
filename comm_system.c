#include "headers/comm_system.h"
#include <unistd.h>
#include <stdio.h>
void *comm_system(void* p)
{
	int readbytes = 0;
	char buffer[161000];
	while((readbytes=read(*(int*)p, buffer, 161000)) > 0)
	{
		write(1, buffer, readbytes );
	}
}
