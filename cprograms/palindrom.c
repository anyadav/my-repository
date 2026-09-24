#include<stdio.h>
#include<string.h>

void checkpalindrom(char *ptr);

int main(){
char str[100]; 
printf("Enter an string to check if palindrom or not: ");
if(scanf("%99s", str) != 1)
	return 1;

checkpalindrom(str);

return 0;
}

void checkpalindrom(char *ptr)
{
int i=0, len=strlen(ptr);

printf("len = %d \n",len);
while(i < len)
{
if(ptr[i++]!=ptr[--len])
{ printf("Its Not palindrom \n");
return;}
}
printf("Its palindrom\n");
}
