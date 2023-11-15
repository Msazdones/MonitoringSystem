#include "headers/comm_system.h"
#include <unistd.h>
#include <stdio.h>
void *comm_system(void* p)
{
	int readbytes = 0;
	char buffer[161000];

	int socket_desc;
    	struct sockaddr_in server_addr;
    	
    	socket_desc = socket(AF_INET, SOCK_STREAM, 0);
	if(socket_desc < 0){
		printf("Unable to create socket\n");
		//return -1;
	}
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(SERVER_PORT);
	server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);

	if(connect(socket_desc, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0){
		printf("Unable to connect\n");
		//return -1;
	}
	printf("Connected with server successfully\n");

	while((readbytes=read(*(int*)p, buffer, 161000)) > 0)
	{
		write(1, buffer, readbytes );
		if(send(socket_desc, buffer, strlen(buffer), 0) < 0){
			printf("Unable to send message\n");
			//return -1;
		}
	}
}
