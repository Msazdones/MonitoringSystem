#include "../headers/probe_body.h"
#include "../headers/server_comm.h"

int main()
{
	int socket_desc;
	
	if(!create_connection(&socket_desc))
	{
		return -1;
	}

	if(!initial_setup(&socket_desc))
	{
		return -1;
	}

	return probe_body(&socket_desc);
}