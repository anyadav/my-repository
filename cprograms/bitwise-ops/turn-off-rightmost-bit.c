#include<stdio.h>

int main()
{
int num;
int turnoffrightmost(int num);
printf("Enter a number to turn off its rightmost bit: ");
scanf("%d",&num);
printf("Number %d after turnning off the right most set bit is %d \n",num,turnoffrightmost(num));

}
int turnoffrightmost(int num)
{
static int count;
if(!(num&1))
{
count++;
 return turnoffrightmost(num>>1);
}
else return (num^1)<<count;
}


