#include<stdio.h>

int fact(int n){
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
scanf("%d",&n);
if(n>0){

printf("Factorial of %d is %d\n",n,fact(n));
}
else
{
 printf("invalid number, please enter a non zero positive number\n");
while(n<=0)
{
printf("Enter valid number: ");
scanf("%d",&n);
}
printf("Factorial of %d is %d\n",n,fact(n));
}
//else
//printf("Factorial of %d is %d\n",n,fact(n));
//printf("\n");
return 0;
}
