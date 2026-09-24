#include<stdio.h>
#include<stdlib.h>
#include<string.h>

int add(int x, int y){

int z =10;
z = x+y;
return z;
}

int main(int argc, char**argv){

if(argc < 3){
	printf("Usage: %s <num1> <num2>\n", argv[0]);
	return 1;
}

int a = atoi(argv[1]);
int b = atoi(argv[2]);

int  c;
char buffer[100];
if(fgets(buffer, sizeof(buffer), stdin) != NULL){
	buffer[strcspn(buffer, "\n")] = '\0';
	puts(buffer);
}

c = add(a,b);

printf("Sum of %d and %d is %d\n", a,b,c);

return 0;
}
