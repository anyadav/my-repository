#include<stdio.h>

int main(){
char str; 
printf("Enter an string to check if palindrom or not: ");
scanf("%s", &str);

checkpalindrom(&str);

}

void checkpalindrom(char *ptr)
{
int i=0, len=strlen(ptr);

printf("len = %d \n",len);
while(len)
{
if(ptr[i++]!=ptr[--len])
{ printf("Its Not palindrom \n");
return;}
}
printf("Its palindrom\n");
}
