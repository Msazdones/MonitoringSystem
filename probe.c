#include "headers/file_lecture.h"
#include "headers/probe.h"

void *probe(void* p)
{
	clock_t begin, end;
	double time_spent = 0;

	DIR *dr; //punteros para lectura de directorios
	struct dirent *en;
	
	int prcnt = 0; //numero de directorios
	struct prrsd *prdata = NULL; //puntero a array de estructuras de datos de los procesos
	
	double hertz = (double)sysconf(_SC_CLK_TCK);
	double totmempages = (double)get_phys_pages();

	int i = 0;
	
	char sending_data[161*MAXPROCS];
		
	while(1)
	{
		prdata = (struct prrsd *)malloc(MAXPROCS * sizeof(struct prrsd));
		dr = opendir(PROCDIR); //open all or present direct
		prcnt = 0;
		begin = clock();
		if(dr) 
		{
			while((en = readdir(dr)) != NULL) //comprueba si ya se han leido todos los dir
			{
				if(isNameNumber(en->d_name)) //comprueba si el directorio es un proceso
				{	
					prcnt++; //cuenta del número de procesos que hay ejecutándose
					if(strlen(en->d_name) <= MAXNAMESIZE) //comprueba el tamaño de nombre de directorio para evitar overflow
					{
						extractPrData(en->d_name, &prdata, prcnt, hertz, totmempages);	
					}
				}
			}
			closedir(dr); //close all directory
		}
		//COMPROBACIÓN
		
		for(i = 0; i < prcnt; i++)
		{
			strcat(sending_data, prdata[i].prname);
			strcat(sending_data, "\n");
			strcat(sending_data, prdata[i].pid);
			strcat(sending_data, "\n");
			strcat(sending_data, prdata[i].rchar);
			strcat(sending_data, "\n");
			strcat(sending_data, prdata[i].wchar);
			strcat(sending_data, "\n");
			strcat(sending_data, prdata[i].status);
			strcat(sending_data, "\n");
			strcat(sending_data, prdata[i].ram);
			strcat(sending_data, "\n");
			strcat(sending_data, prdata[i].cpu);
			strcat(sending_data, "\n\n");
			//printf("%s: %s, %s, %s, %c, %s, %s\n", prdata[i].prname, prdata[i].pid, prdata[i].rchar, prdata[i].wchar, prdata[i].status, prdata[i].ram, prdata[i].cpu);
		}
		//printf("%s\n", sending_data);
		
		write(*(int*)p, sending_data, strlen(sending_data));
	
		free(prdata);
		prdata = NULL;
		
		end = clock();
		time_spent = (double)(end - begin) / CLOCKS_PER_SEC;
		printf("%lf\n",time_spent);
		sleep(5);
	}
}
