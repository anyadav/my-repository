#include<stdio.h>

/* defined in myfun.c */
int add(int a, int b);
int diff(int a, int b);
int mul(int a, int b);

int main()
{


int a =10;
int b =20;
int c=10;

int ad,dif,mult,dif1;
mult = mul(a,b);
ad = add(a,b);
dif = diff(a,b);
dif1 = diff(a,c);
printf("add: %d\ndiff: %d\ndiff1: %d\nmul: %d\n",ad,dif,dif1,mult);

return 0;
}
