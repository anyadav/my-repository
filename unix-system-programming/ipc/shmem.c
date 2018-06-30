#include<stdio.h>
#include<stdlib.h>
#include<sys/shm.h>
#include<sys/ipc.h>

#define SHMSIZE 1024

int
main ()
{
  int shmid;
void *shm_mem = (void *)0;

  shmid = shmget ((key_t) 1234, SHMSIZE, 0666 | IPC_CREAT);
  printf("shared mem id: %d\n", shmid);

  shm_mem = shmat (shmid, (void *) 0, 0);
  printf("Shared memory at address: %x\n", (unsigned int)shm_mem);

  shmdt (shm_mem);
  printf("shared memory is detached now\n");
  shmctl (shmid, IPC_RMID, 0);
  printf("shared memory is deleted now\n");



}
