#include<stdio.h>

int main()
{
/*
int *ptr = (int *)malloc(110);

char **q=&ptr;
printf("vddress starts at:%lu\n",ptr);
if(ptr)
{printf("memory allocated!!\n");
}
printf("value at q is :%lu\n",*q);
*/
	char *str;
        str = (char*) malloc(sizeof(char)*1000);
        int *length;
        length = str-4; /*because on 32 bit system, an int is 4 bytes long*/
        printf("Length of str:%d\n", *length);
        free(str);

return 0;
}

