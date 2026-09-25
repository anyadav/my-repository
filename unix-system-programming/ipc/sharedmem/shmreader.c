#include<stdio.h>
#include<stdlib.h>
#include<sys/ipc.h>
#include<sys/shm.h>

int main()
{

int k, shmid;
void *data;
k = ftok("./amar",10);

shmid = shmget(k,1000,0);
data = shmat(shmid, (void *)0,0);

printf("\n %s\n",(char *)data);

data +=10;

printf("\n %s\n",(char *)data);
shmdt(data);

/* reader runs last in this reader/writer pair, so it releases the
   shared-memory segment the writer created */
shmctl(shmid, IPC_RMID, 0);

exit(0);

}
