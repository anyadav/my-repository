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
	size_t len = 1000;
	char *str;
        str = (char*) malloc(sizeof(char)*len);
        if(str == NULL)
                return 1;
        /* Track the requested size ourselves instead of reading malloc's
           internal chunk-size header: that header is an allocator
           implementation detail, not part of the object malloc() returns,
           so reading the bytes before the pointer is undefined behavior
           (and is flagged by AddressSanitizer as a heap-buffer-overflow). */
        printf("Length of str:%zu\n", len);
        free(str);

return 0;
}

