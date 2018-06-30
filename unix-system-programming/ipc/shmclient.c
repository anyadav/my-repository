#include<stdio.h>
#include<stdlib.h>
#include<sys/shm.h>
#include<sys/ipc.h>

#define SHMSIZE 1024
#define BUFFSIZE 30
int
main ()
{
  int shmid, i =0 ;
  
void *shm_mem = (void *) 0;
char buff[BUFFSIZE];
char *sm;

  shmid = shmget ((key_t) 1234, SHMSIZE, 0666 | IPC_CREAT);
  shm_mem = shmat (shmid, (void *) 0, 0);


//Read data from shared memory
  sm = (char *)shm_mem;
while(*sm)
{
buff[i++] = *(char *)sm++;
}    

*sm = (char *)NULL;
*(char *)shm_mem = '*';
//shm_mem =NULL;

//  printf ("buff: %s\n shared mem contains:%s\n",(char *)buff, (char *)shm_mem);
  shmdt (shm_mem);
  printf ("shared memory is detached now\n");
//  shmctl (shmid, IPC_RMID, 0);
//  printf ("shared memory is deleted now\n");



}
