#include<stdio.h>


int main(){

unsigned int a, count1,temp;
int count = 0;
int countsetbits(unsigned int num);
printf("Enter the number to count set bits: ");
scanf("%u",&a);
temp = a;

//Method 1 : Using loop
while(a){
if(a&1)count++;
a=a>>1;
}
printf("No one set bits: %d\n",count);



a=temp;
count1 = countsetbits(a);
printf("Total 1s in %u is: %u \n",a,count1);

return 0;
}


//Method 2 : Without loop

int countsetbits(unsigned int num)
{
if(num==0)
	return 0;
else
	return ((num&1) + countsetbits(num>>1)); //add 1 if bit is 1 else add 0
}
