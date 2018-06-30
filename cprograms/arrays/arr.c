#include<stdio.h>

struct amar
{
long double ln;
char ch;
long ln1;
short int si;
int a;
};
struct amar an;





int main()
{
int *p;
int i;
int a[5]={1,2,3,4,5};
p=a;
for(i=0;i<5;i++)
{
printf("%d %d %d %d %d\n",a[i],*p,*(a+i),*(&a[0] +i),p[0]);
p++;
p--;
printf("\n%d\n",*p);
p++;
}

an.a =5;
an.ch = 'a';
an.ln=1234567;
an.si =1;


printf("long: %d\n",sizeof(long));
printf("int: %d\n",sizeof(int));
printf("char: %d\n",sizeof(char));
printf("short: %d\n",sizeof(short));
printf("long double: %d\n",sizeof(long double));
printf("\n size of struct: %d\n",sizeof(an));
/*
for(i=4;i>=0;i--)
{

printf("%d %d %d %d\n",a[i],*p,*(a+i),*(&a[0] +i));
p--;
}
*/
return 0;

}

