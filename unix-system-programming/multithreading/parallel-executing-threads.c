#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
#include<string.h>
#include<pthread.h>

void *threadfun (void *arg);
void *thrfun1 (void *arg);
void *thrfun2 (void *arg);
void errchk (int err);


/*Message passing between threads */
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





/*checking parallel execution of threads */

  res = pthread_create (&thread1, NULL, thrfun1, (void *) NULL);
  errchk (res);
  res = pthread_create (&thread2, NULL, thrfun2, (void *) NULL);
  errchk (res);


  res = pthread_join (thread1, &threadres);
  errchk (res);
  res = pthread_join (thread2, &threadres);
  errchk (res);

  res = pthread_join (athread, &threadres);
  errchk (res);

  printf ("Thread joined, it returned:\n%s\n", (char *) threadres);
  printf ("msg is now:\n%s\n", msg);
  printf ("\n");


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
threadfun (void *arg)
{
  printf ("Running thread function, argument passed is:\n%s\n", (char *) arg);
  strcpy (msg, "Hello from threadfun");
  pthread_exit ("Thanks you for CPU Time");
}


void *
thrfun1 (void *arg)
{
  int count = 0;
  while (count++ < 1000)
    {
      printf ("1");
    }
}




void *
thrfun2 (void *arg)
{
  int count = 0;
  while (count++ < 1000)
    {
      printf ("2");
    }
}
