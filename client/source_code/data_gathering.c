#include "../headers/data_gathering.h"

void data_gathering(char **data)
{
	const char DATAFILES[4][7] = {"stat", "status", "io", "fd"};
	char file_route[100], fdfile[100];
	char file_buffer[BUFFER_SIZE], fdbuff[100];
	
	DIR *dr, *fddir;
	struct dirent *en;
	
	int prcnt = 0, i = 0;
	
	FILE *fp;	//puntero para lectura de archivos
	
	//obtener fecha y hora de la medida
	char aux[40];
	time_t t = time(NULL);
	struct tm tstamp = *localtime(&t);

	struct sysinfo s_info;
	sysinfo(&s_info);

	sprintf(aux, "%d-%02d-%02d %02d:%02d:%02d", tstamp.tm_year + 1900, tstamp.tm_mon + 1, tstamp.tm_mday, tstamp.tm_hour, tstamp.tm_min, tstamp.tm_sec);
	strncat((*data), aux, strlen(aux));
	
	memset(aux,0,strlen(aux));
	
	sprintf(aux, "%ld", s_info.uptime);
	strncat((*data), aux, strlen(aux));
	strncat((*data), "||\n", 4);

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

					if(strcmp(DATAFILES[i], "fd") != 0)
					{
						fp = fopen(file_route, "r");
						
						if(fp == NULL)
						{
							break;
						}

						fread(file_buffer, BUFFER_SIZE, 1, fp);
						fclose(fp);
					}
					else
					{
						fddir = opendir(file_route);
						
						if(fddir)
						{	
							while((en = readdir(fddir)) != NULL)
							{
								if(isNameNumber(en->d_name))
								{
									memset(fdfile,0,strlen(fdfile));
									memset(fdbuff,0,strlen(fdbuff));

									strcat(fdfile, file_route);
									strcat(fdfile, "/");
									strcat(fdfile, en->d_name);

									readlink(fdfile, fdbuff, 100);
									
									strcat(file_buffer, fdbuff);
									strcat(file_buffer, "\n");
								}
							}
						}
						closedir(fddir);
					}
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