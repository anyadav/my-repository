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

/* read at offset 10 without moving data, so shmdt gets the attach address */
printf("\n %s\n",(char *)data + 10);
shmdt(data);

/* reader runs last in this reader/writer pair, so it releases the
   shared-memory segment the writer created */
shmctl(shmid, IPC_RMID, 0);

exit(0);

}
