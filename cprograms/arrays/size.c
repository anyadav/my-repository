#include<stdio.h>

struct amar
{
long double ln;
char ch;
int a;
long ln1;
char ch1;
//short int si;
//char ch1;
};
struct amar an;

int main()
{

printf("long: %d\n",sizeof(long));
printf("int: %d\n",sizeof(int));
printf("char: %d\n",sizeof(char));
printf("short: %d\n",sizeof(short));
printf("long double: %d\n",sizeof(long double));

printf("\n size of struct: %d\n",sizeof(an));
return 0;

}

