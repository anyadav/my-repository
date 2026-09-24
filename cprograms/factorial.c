#include<stdio.h>

/* unsigned long long holds factorials up to 20! */
unsigned long long fact(int n){
if(n==0) return 1;
else if (n==1) return 1;
else{
return n*fact(n-1);
}
}

int main()
{
int n;
printf("Enter number to calculate its factorial: ");
if(scanf("%d",&n) != 1) return 1;
if(n>0 && n<=20){

printf("Factorial of %d is %llu\n",n,fact(n));
}
else
{
 printf("invalid number, please enter a positive number from 1 to 20\n");
while(n<=0 || n>20)
{
printf("Enter valid number: ");
if(scanf("%d",&n) != 1) return 1;
}
printf("Factorial of %d is %llu\n",n,fact(n));
}
//else
//printf("Factorial of %d is %d\n",n,fact(n));
//printf("\n");
return 0;
}
