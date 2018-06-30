#include <stdio.h>
#include<stdlib.h>
#include<errno.h>

#include<sys/types.h>
#include<sys/sem.h>
#include<sys/ipc.h>

int main()
{

key_t key = (key_t)1234;
int semid;

int sem;

struct sembuf sb = {0, 1,0};


union semun {
               int              val;    /* Value for SETVAL */
               struct semid_ds *buf;    /* Buffer for IPC_STAT, IPC_SET */
               unsigned short  *array;  /* Array for GETALL, SETALL */
               struct seminfo  *__buf;  /* Buffer for IPC_INFO
                                           (Linux-specific) */
           }arg;


//grab the semaphore
semid = semget(key,1,0);
if(semid < 0)
{
printf("semget failed!!!\n");
perror("semget");
exit(1);
}
else printf("semaphore id: %d\n", semid);



//Do the semop 
printf("Before locking: \nsem_num:%d\nsem_op:%d\nsem_flg:%d\n",sb.sem_num,sb.sem_op,sb.sem_flg);
sem = semop(semid,&sb,1);
if(sem < 0)
{
printf("semop failed!!!\n");
perror("semop");
perror("semop");
exit(1);
}

printf("locked\n");
printf("After locking: \nsem_num:%d\nsem_op:%d\nsem_flg:%d\n",sb.sem_num,sb.sem_op,sb.sem_flg);

printf("Before unlocking: \nsem_num:%d\nsem_op:%d\nsem_flg:%d\n",sb.sem_num,sb.sem_op,sb.sem_flg);
sb.sem_op = 1;
sem = semop(semid, &sb,1);
if(sem < 0)
{
printf("semop failed!!!!\n");
perror("semop");
exit(2);
}
printf("unlocked\n");
printf("After unlocking: \nsem_num:%d\nsem_op:%d\nsem_flg:%d\n",sb.sem_num,sb.sem_op,sb.sem_flg);

//Removing allocated semaphore

sem = semctl(semid, 0, IPC_RMID, &arg);
if(sem < 0)
{
printf("semctl failed while removing semaphore!!!\n");
perror("semctl");
exit(3);
}


return 0;

}
