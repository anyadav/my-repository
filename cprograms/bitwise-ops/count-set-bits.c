#include<stdio.h>


int main(){

int a;
static int count = 0;
printf("Enter the number to count set bits: ");
scanf("%d",&a);
do{
if(a==0)return 0;
else if(a&1)count++;
a=a>>1;
}while(a);
printf("No. of set bits: %d\n",count);

return 0;
}

