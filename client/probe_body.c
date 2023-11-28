#include "headers/probe_body.h"
#include "headers/data_gathering.h"

int probe_body(int *socket_desc)
{
	int sending_data_len = 0;
	char *sending_data;
	char command[20];

	sending_data = (char*)malloc(BUFFER_SIZE * MAX_PROCS_TO_EVAL * sizeof(char));

	while(1)
	{
		memset(sending_data, 0, strlen(sending_data));
		memset(command, 0, strlen(command));

		data_gathering(&sending_data);

		sending_data_len = strlen(sending_data);
		sprintf(command, "%d", sending_data_len);
		send((*socket_desc), &command, strlen(command), 0);
		memset(command, 0, strlen(command));

		recv((*socket_desc), command, strlen(command)-1, 0);

		if(strcmp(command, ACK_MSG))
		{
			printf("Fallo en la recepción. Abortando.\n");
			return -1;
		}

		if(send((*socket_desc), sending_data, strlen(sending_data), 0) < 0)
		{
			printf("Fallo al enviar los datos\n");
			return -1;
		}
		sleep(5);	
	}
	return 0;
}

int initial_setup(int *socket_desc)
{
	char data[100], aux[20];

	int hertz = sysconf(_SC_CLK_TCK);
	int totmempages = get_phys_pages();
	struct sysinfo s_info;
    sysinfo(&s_info);

	memset(data,0,strlen(data));

	data[0] = '(';
	sprintf(aux, "%ld", s_info.uptime);
	strncat(data, aux, strlen(aux));
	strncat(data, ",", 2);
	sprintf(aux, "%d", hertz);
	strncat(data, aux, strlen(aux));
	strncat(data, ",", 2);
	sprintf(aux, "%d", totmempages);
	strncat(data, aux, strlen(aux));
	strncat(data, ")", 2);

	printf("%s\n",data);

	if(send(*socket_desc, data, strlen(data), 0) < 0)
	{
		printf("Fallo al enviar los datos\n");
		return 0;
	}
	memset(data,0,strlen(data));
	
	recv(*socket_desc, data, strlen(data)-1, 0);

	if(strcmp(data, ACK_MSG)) //si no son iguales, return error
	{
		return 0;
	}

	return 1;
}