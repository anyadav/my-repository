#include<sys/ipc.h>
#include<sys/shm.h>

int main()
{

int k, shmid;
void *data;
k = ftok("./amar",10);

shmid = shmget(k,1000,0);
data = shmat(shmid, (void *)0,0);

printf("\n %s\n",data);

data +=10;

printf("\n %s\n",data);
shmdt(data);

exit(0);

}
