#include<stdio.h>
#include<stdlib.h>
#include<sys/shm.h>
#include<sys/ipc.h>

#define SHMSIZE 1024

int
main ()
{
  int shmid;
  char c;
  void *shm_mem = (void *) 0;
  void *sm;

  shmid = shmget ((key_t) 1234, SHMSIZE, 0666 | IPC_CREAT);
  shm_mem = shmat (shmid, (void *) 0, 0);

//print detail of created shared memory before writing anything
  printf ("value written in shared mem is: %s\n", (char *) shm_mem);

//Write something to memory
  sm = shm_mem;
  for (c = 'a'; c <= 'z'; c++)
    {
      *(char *) sm++ = c;
    }
  *(char *)sm = '\0';
//See what you have written
  printf ("value written in shared mem is: %s\n", (char *) shm_mem);

while(*(char *)shm_mem != '*')
{
printf("%c", *(char *)shm_mem);
sleep(10);
}
  printf ("value in shared mem after read from client: %s\n", (char *) shm_mem);
  shmdt (shm_mem);
  printf ("shared memory is detached now\n");
  shmctl (shmid, IPC_RMID, 0);
  printf ("shared memory is deleted now\n");



}
