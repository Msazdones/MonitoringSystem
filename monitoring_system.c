#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include "headers/probe.h"
#include "headers/comm_system.h"

#define NTHREATHS 2

int main(void) 
{
	pthread_t thread_ids[NTHREATHS];
	int i = 0, p[2];
	
	pipe(p);
	
	printf("%d %d\n", p[0], p[1]); 
	pthread_create(&thread_ids[0], NULL, probe, &p[1]);
	pthread_create(&thread_ids[1], NULL, comm_system, &p[0]);
	
	for(i = 0; i < NTHREATHS; i++)
	{
		pthread_join(thread_ids[i], NULL);	
	} 	
	
	return 0;
}
