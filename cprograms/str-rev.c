#include<stdio.h>
#include<string.h>

char revstr[20];

void
reverse (char *strng)
{
static int i=0;
  if (*strng)
    {
      reverse (strng + 1);
      revstr[i++] = *strng;	
    }
}


int
main ()
{
  char str[] = "amarnathyadav";
  reverse (str);
      printf("\n%s\n",revstr);
  return 0;
}
