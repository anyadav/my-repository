#include<stdio.h>
#include<stdlib.h>

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
        if(str == NULL)
                return 1;
        size_t *length;
        /* glibc keeps the chunk size in the size_t just before the returned
           pointer (8 bytes on 64 bit, not 4). The low 3 bits are flags, so
           mask them off. The size includes malloc's header and padding. */
        length = (size_t *)(str - sizeof(size_t));
        printf("Length of str:%zu\n", *length & ~(size_t)7);
        free(str);

return 0;
}

