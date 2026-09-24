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
      if (i < (int) sizeof (revstr) - 1)
        revstr[i++] = *strng;
      revstr[i] = '\0';
    }
  else
    {
      i = 0;	/* deepest call runs first: reset for each new string */
      revstr[0] = '\0';
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
