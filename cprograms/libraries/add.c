#include<stdio.h>

int add(int a, int b); /* defined in mylib.c (mylibrary.so) */

int main(){

int k;//,i=j=5;
k = add(5,6);
printf("Additin: %d\n",k);

return 0;

}


