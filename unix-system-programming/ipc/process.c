#include<unistd.h>
#include<stdio.h>
#include<stdlib.h>
#include<sys/types.h>
#include<sys/wait.h>

#define COUNT 100

void
ERRORHANDLE ()
{
  printf ("process creation failed!!!");
  abort ();
}




int main ()
{

  pid_t pid[100];
  int i = 0;
  while (i++ < COUNT)
    {
      pid[i] = fork ();
      if (pid[i] < 0)
	{
	  ERRORHANDLE ();
	}
      else if (pid[i] == 0)
	{
	  printf ("child:%d  %d  %s %s\n", i, getpid (), __DATE__, __TIME__);
	  exit (0);
	}
      else if (pid[i] > 0)
	{

	  wait (NULL);
	}

    }
  return 0;

}

