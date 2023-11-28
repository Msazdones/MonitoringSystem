#include "headers/probe_system.h"

int main()
{
	int sending_data_len = 0;
	char *sending_data;
	char command[20];

	sending_data = (char*)malloc(BUFFER_SIZE * MAX_PROCS_TO_EVAL * sizeof(char));

	int socket_desc;
	struct sockaddr_in server_addr;	
	
	if(!create_connection(&socket_desc, &server_addr))
	{
		return -1;
	}

	if(!initial_setup(&socket_desc))
	{
		return -1;
	}
	
	while(1)
	{
		memset(sending_data, 0, strlen(sending_data));
		memset(command, 0, strlen(command));

		gathering_data(&sending_data);

		sending_data_len = strlen(sending_data);
		sprintf(command, "%d", sending_data_len);
		send(socket_desc, &command, strlen(command), 0);
		memset(command, 0, strlen(command));

		recv(socket_desc, command, strlen(command)-1, 0);

		if(strcmp(command, ACK_MSG))
		{
			printf("Fallo en la recepción. Abortando.\n");
			return -1;
		}

		if(send(socket_desc, sending_data, strlen(sending_data), 0) < 0)
		{
			printf("Fallo al enviar los datos\n");
			return -1;
		}
		printf("aaaa\n");
		sleep(5);	
	}
	return 0;
}

int initial_setup(int *socket_desc)
{
	char data[100], aux[20];

	int hertz = sysconf(_SC_CLK_TCK);
	int totmempages = get_phys_pages();

	FILE *fp;
	fp = fopen(UPFILE, "r");
	float uptime = 0;
	fread(aux, strlen(aux), 1, fp);
	fclose(fp);

	memset(data,0,strlen(data));

	data[0] = '(';
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

int create_connection(int *socket_desc, struct sockaddr_in *server_addr)
{
	*socket_desc = socket(AF_INET, SOCK_STREAM, 0);
	
	if(socket_desc < 0){
		printf("Fallo en la creación del socket\n");
		return 0;
	}
	(*server_addr).sin_family = AF_INET;
	(*server_addr).sin_port = htons(SERVER_PORT);
	(*server_addr).sin_addr.s_addr = inet_addr(SERVER_IP);

	if(connect(*socket_desc, (struct sockaddr*)&(*server_addr), sizeof((*server_addr))) < 0){
		printf("Fallo en el establecimiento de la comunicación\n");
		return 0;
	}
	printf("Conexión con el servidor central realizada con éxito\n");

	return 1;
}

void gathering_data(char **data)
{
	const char DATAFILES[3][6] = {"stat", "statm", "io"};
	char file_route[100];
	char file_buffer[BUFFER_SIZE];
	
	DIR *dr;
	struct dirent *en;
	
	int prcnt = 0, i = 0;
	
	FILE *fp;	//puntero para lectura de archivos
	
	prcnt = 0;
	dr = opendir(PROC_DIR);
	if(dr) 
	{
		while((en = readdir(dr)) != NULL) //comprueba si ya se han leido todos los dir
		{
			if(isNameNumber(en->d_name)) //comprueba si el directorio es un proceso
			{	
				prcnt++; //cuenta del número de procesos que hay ejecutándose
				for(i = 0; i < FILES_TO_EVAL; i++)
				{
					memset(file_buffer,0,strlen(file_buffer));
					
					strcpy(file_route, PROC_DIR);
					strcat(file_route, en->d_name);
					strcat(file_route, "/");
					strcat(file_route, DATAFILES[i]);
					
					fp = fopen(file_route, "r");
					fread(file_buffer, BUFFER_SIZE, 1, fp);
					fclose(fp);

					strcat((*data), file_buffer);
					strcat((*data), "||\n");
				}	
			}
			if(prcnt >= MAX_PROCS_TO_EVAL)
			{
				break;
			}
		}
	}
	closedir(dr); //close all directory
}

int isNameNumber(char * name)
{
	int l = 0, i = 0;
	
	l = strlen(name);
	for(i=0; i<l; i++)
	{
		if(!isdigit(name[i]))
		{
			return 0;
		}
	}
	return 1;
}



