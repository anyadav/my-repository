#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
#include<string.h>
#include<errno.h>
#include<pthread.h>
#include<semaphore.h>

void *threadfun (void *arg);
void *thrfun1 (void *arg);
void *thrfun2 (void *arg);
void *thrfun3 (void *arg);
void *thrfun4 (void *arg);
void *thrfun5 (void *arg);
void errchk (int err);


/* To use semaphore */

sem_t sem;
int semid,err;
static int shrd_val = 0;
static int errcount = 0;


int
main ()
{

  int res;
  pthread_t athread, thread1, thread2, thread3,thread4,thread5;
  void *threadres;



//initialize semaphore
  semid = sem_init (&sem, 0, 0);
  errchk (semid);


/*checking paraller execution of threads */

  res = pthread_create (&thread1, NULL, thrfun1, (void *) NULL);
  errchk (res);
  res = pthread_create (&thread2, NULL, thrfun2, (void *) NULL);
  errchk (res);
  res = pthread_create (&thread3, NULL, thrfun3, (void *) NULL);
  errchk (res);
  res = pthread_create (&thread4, NULL, thrfun4, (void *) NULL);
  errchk (res);
  res = pthread_create (&thread5, NULL, thrfun5, (void *) NULL);
  errchk (res);
  

  res = pthread_join (thread1, &threadres);
  errchk (res);
  res = pthread_join (thread2, &threadres);
  errchk (res);
  res = pthread_join (thread3, &threadres);
  errchk (res);
  res = pthread_join (thread4, &threadres);
  errchk (res);
  res = pthread_join (thread5, &threadres);
  errchk (res);


  printf ("\n");

  printf ("shrd_val: %d \nerrcount: %d\n", shrd_val, errcount);


  return 0;
}


void
errchk (int err)
{
  if (err != 0)
    {
      perror ("failed");
      exit (EXIT_FAILURE);
    }
}



void *
thrfun1 (void *arg)
{
  int count = 0;
//  if (sem_trywait (&sem) == EAGAIN)
  err = sem_trywait (&sem);
if(err < 0)
    errcount++;
  while (count++ < 1000)
    {
      printf ("1");
      shrd_val++;
    }
  sem_post (&sem);
}


void *
thrfun2 (void *arg)
{
  int count = 0;
  err = sem_trywait (&sem);
if(err < 0)
    errcount++;
  while (count++ < 1000)
    {
      printf ("2");
      shrd_val++;
    }
  sem_post (&sem);
}

void *
thrfun3 (void *arg)
{
  int count = 0;
  err = sem_trywait (&sem);
if(err < 0)
    errcount++;
  while (count++ < 1000)
    {
      printf ("3");
      shrd_val++;
    }
  sem_post (&sem);
}


void *
thrfun4 (void *arg)
{
  int count = 0;
  err = sem_trywait (&sem);
if(err < 0)
    errcount++;
  while (count++ < 1000)
    {
      printf ("4");
      shrd_val++;
    }
  sem_post (&sem);
}


void *
thrfun5 (void *arg)
{
  int count = 0;
  err = sem_trywait (&sem);
if(err < 0)
    errcount++;
  while (count++ < 1000)
    {
      printf ("5");
      shrd_val++;
    }
  sem_post (&sem);
}
