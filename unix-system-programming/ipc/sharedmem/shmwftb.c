#include<sys/ipc.h>
#include<sys/shm.h>

int main()
{

int k, shmid;
void *data;
FILE *fp;
char buf[100];

k=ftok("./amar",10);

shmid = shmget(k, 1000, IPC_CREAT | 0744);
data = shmat(shmid, (void *)0, 0);



strcpy((char*)tmp, "helloWorld");

shmdt(data);
exit(0);
}


