#include "headers/file_lecture.h"

//función para extraer las medidas de los archivos 
void extractPrData(char strpid[], struct prrsd **prdata, int prcnt, double hertz, double totmempages)
{
	const char DATAFILES[3][6] = {"stat", "statm", "io"};

	FILE *fp;	//puntero para lectura de archivos
	char txtbuffer[BUFFERSIZE]; //buffer para lectura de archivos
	char filepath[MAXPATHSIZE]; //string con el filepath completo de cada proceso
	int i = 0, j = 0, k = 0;
	char *data = NULL;

	float utime = 0, stime = 0, cutime = 0, cstime = 0, starttime = 0, uptime = 0, total_time = 0, prseconds = 0;
	
	gcvt(atoi(strpid), 15, (*prdata)[prcnt-1].pid);
	
	//bucle para recorrer los archivos que haya que elegir para tomar las medidas
	fp = fopen(UPFILE, "r");
	fread(txtbuffer, BUFFERSIZE, 1, fp);
	data = strtok(txtbuffer, " ");
	uptime = atof(data);
	fclose(fp);
	
	for(i = 0; i<DATAFILESCNT; i++)
	{
		//creación del path de cada archivo 
		strcpy(filepath, PROCDIR);
		strcat(filepath, strpid);
		strcat(filepath, "/");
		strcat(filepath, DATAFILES[i]);
		
		//apertura de archivo
		fp = fopen(filepath, "r");
		
		//En función de cada archivo habrá que tratarlo de diferentes maneras 
		switch(i)
		{
			//cada case lee una linea y separa la información en función de de un delimitador (" " o "\n")
			//Depués, una vez separada la información, iteración a iteración por cada sub cadena se obtiene el dato y se opera con el o se guarda
			case 0:
				fread(txtbuffer, BUFFERSIZE, 1, fp);
				data = strtok(txtbuffer, " ");
				for(k = 0; k < 22; k++)
				{
					switch(k)
					{
						//cada uno de estos casos se recupera el dato que se quiera
						//Para ver las posiciones de cada dato consultar man proc
						case 1:
							memmove(data, data + 1, strlen(data));
							strcpy((*prdata)[prcnt-1].prname, data);
							break;
						case 2:
							(*prdata)[prcnt-1].status[0] = data[0];
							break;
						case 13:
							utime = atof(data);
							break;
						case 14:
							stime = atof(data);
							break;
						//esto es en caso de querer añadir el tiempo de procesos hijos, de momento no
						/*case 15:
							cutime = atoi(data);
							break;
						case 16:
							cstime = atoi(data);
							break;*/
						case 21:
							starttime = atof(data);
							total_time = utime + stime + cutime + cstime;
							prseconds = uptime - (starttime / hertz);
							gcvt(roundf(100 * ((total_time / hertz) / prseconds)), 10, (*prdata)[prcnt-1].cpu);
							break;
						default:
							break;

					}
					
					if(k == 0)
					{
						data = strtok(NULL, ")");
					}
					else
					{
						data = strtok(NULL, " ");
					}
				}
				break;
			case 1:
				fread(txtbuffer, BUFFERSIZE, 1, fp);
				data = strtok(txtbuffer, " ");
				for(k = 0; k < 6; k++)
				{
					switch(k)
					{
						case 1:
							gcvt(roundf((float)(atof(data)/totmempages)), 10, (*prdata)[prcnt-1].ram);
							break;
						default:
							break;
					}
				}
				break;
			case 2:
				fread(txtbuffer, BUFFERSIZE, 1, fp);
				data = strstr(txtbuffer, "rchar:");
				data = strtok(data, "\n");
				data = strstr(data, " ");
				gcvt(atoi(data), 10, (*prdata)[prcnt-1].rchar);
				
				fread(txtbuffer, BUFFERSIZE, 1, fp);
				data = strstr(txtbuffer, "wchar:");
				data = strtok(data, "\n");
				data = strstr(data, " ");
				gcvt(atoi(data), 10, (*prdata)[prcnt-1].wchar);
				break;
			default:
				break;
		}
		fclose(fp);
	}

}
	
//Esta función se encarga de comprobar si una cadena de texto pasada como argumento es un número entero o no
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
