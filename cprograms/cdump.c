int add(int x, int y){

int z =10;
z = x+y;
return z;
}

int main(int argc, char**argv){

int a = atoi(argv[1]);
int b = atoi(argv[2]);

int  c;
char buffer[100];
gets(buffer);
puts(buffer);

c = add(a,b);

printf("Sum of %d and %d is %d\n", a,b,c);

return 0;
}
