#include<stdio.h>


int main(){

int a, count1,temp;
int count = 0;
int countsetbits(int num);
printf("Enter the number to count set bits: ");
scanf("%d",&a);
temp = a;

//Method 1 : Using loop
do{
if(a==0)return 0;
else if(a&1)count++;
a=a>>1;
}while(a);
printf("No one set bits: %d\n",count);



a=temp;
count1 = countsetbits(a);
printf("Total 1s in %d is: %d \n",a,count1);

return 0;
}


//Method 2 : Without loop

int countsetbits(int num)
{
if(num==0)
	return 0;
else
	return ((num&1) + countsetbits(num>>1)); //add 1 if bit is 1 else add 0
}
