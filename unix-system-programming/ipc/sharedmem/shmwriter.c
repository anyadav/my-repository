#include<sys/ipc.h>
#include<sys/shm.h>

int main()
{

int k, shmid;
void *data;
char *tmp;

k=ftok("./amar",10);

shmid = shmget(k, 1000, IPC_CREAT | 0744);

data = shmat(shmid, (void *)0, 0);
tmp = (char *)data;
tmp +=10;
strcpy((char*)tmp, "helloWorld");

shmdt(data);
exit(0);
}


