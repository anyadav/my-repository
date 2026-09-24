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

printf("long: %zu\n",sizeof(long));
printf("int: %zu\n",sizeof(int));
printf("char: %zu\n",sizeof(char));
printf("short: %zu\n",sizeof(short));
printf("long double: %zu\n",sizeof(long double));

printf("\n size of struct: %zu\n",sizeof(an));
return 0;

}

