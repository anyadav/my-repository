#include<stdio.h>

int main()
{
int num;
int turnoffrightmost(int num);
printf("Enter a number to turn off its rightmost bit: ");
scanf("%d",&num);
printf("Number %d after turnning off the right most set bit is %d \n",num,turnoffrightmost(num));

return 0;
}
int turnoffrightmost(int num)
{
static int count;
int result;
if(num == 0) //no set bit to turn off
{
count = 0;
return 0;
}
if(!(num&1))
{
count++;
 return turnoffrightmost(num>>1);
}
result = (int)((unsigned int)(num^1)<<count);
count = 0; //reset for the next call
return result;
}


