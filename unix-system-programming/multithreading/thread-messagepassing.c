#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
#include<string.h>
#include<pthread.h>

void *threadfun (void *arg);
void *thrfun1 (void *arg);
void *thrfun2 (void *arg);
void errchk (int err);


char msg[] = "This is just a message to/from thread";

int
main ()
{

  int res;
  pthread_t athread, thread1, thread2;
  void *threadres;


  res = pthread_create (&athread, NULL, threadfun, (void *) msg);
  errchk (res);
  printf ("Waiting for thread to finish!!!\n");

  res = pthread_join (athread, &threadres);
  errchk (res);

  printf ("Thread joined, it returned:\n%s\n", (char *) threadres);
  printf ("msg is now:\n%s\n", msg);


  return 0;

}


void
errchk (int err)
{
  if (err != 0)
    {
      perror ("Thread creation failed");
      exit (EXIT_FAILURE);
    }
}

void *
threadfun (void *arg)
{
  printf ("Running thread function, argument passed is:\n%s\n", (char *) arg);
  sleep (5);
  strcpy (msg, "Hello from threadfun");
  pthread_exit ("Thanks you for CPU Time");
}
