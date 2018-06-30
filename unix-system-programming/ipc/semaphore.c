#include<stdio.h>
#include<stdlib.h>
#include<errno.h>

#include<sys/types.h>
#include<sys/ipc.h>
#include<sys/sem.h>

int main()
{

key_t key = (key_t)1234;
int semid;

int sem;

union semun {
               int              val;    /* Value for SETVAL */
               struct semid_ds *buf;    /* Buffer for IPC_STAT, IPC_SET */
               unsigned short  *array;  /* Array for GETALL, SETALL */
               struct seminfo  *__buf;  /* Buffer for IPC_INFO
                                           (Linux-specific) */
           }arg;



//create semaphore
semid = semget(key, 1, 0666 | IPC_CREAT);
if(semid <0){
perror("semget");
exit(1);
}
else
printf("semget succeded, semid: %d, arg.val:%d\n", semid,arg.val);


//initialize semaphore to 1
arg.val = 1;
printf("arg.val:%d\n", arg.val);
sem = semctl(semid, 0,SETVAL, arg);
if(sem < 0){
perror("semctl");
exit(1);
}

//TO-DO: explore how you can read all values set by GETALL, GETVAL etc
//sem = semctl(semid, 0,GETALL, arg);
//printf("All val: %s\n", arg.array);



return 0;



}
