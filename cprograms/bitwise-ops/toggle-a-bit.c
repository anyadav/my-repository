#include<stdio.h>

int main(){

int num,pos;
int temp=1;
printf("enter a number to toggle its bit: ");
scanf("%d",&num);
printf("Enter the position to be toggled:");
scanf("%d",&pos);

temp = temp<<pos;

printf("numbers before toggleing: num=%d, temp=%d,pos=%d\n",num,temp,pos);
num = num^temp;
printf("number after toggling %dth position is %d\n",pos,num);
return 0;
}
