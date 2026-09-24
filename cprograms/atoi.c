#include<stdio.h>
#include<stdlib.h>

int main()
{
int i;
char buf[256];
printf("Enter a number: ");
if(scanf("%255s",buf) != 1)
	return 1;

i = atoi(buf);
printf("%d\n",i);

return 0;
}

