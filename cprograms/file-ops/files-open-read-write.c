#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>

/*Example program to use open() */
void myopen()
{
int ret;
char c;
char buff[20]= {'a','m','a','r',' ','n','a','t','h',' ','y','a','d','v'};
char rbuff[20];


int fdes;
fdes = open("myfile", O_RDWR|O_CREAT,S_IRUSR|S_IWUSR);
//fdes = open("myfile", O_WRONLY|O_CREAT,S_IRUSR|S_IWUSR);
//fdes = open("myfile", O_RDWR|O_CREAT);

//system("cat myfile");
ret = write (fdes,buff, 14);
if(ret < 0)printf("write() failed!!!ret = %d\n",ret);

lseek(fdes,0,SEEK_SET);
printf("date written by write() into myfile from buff\n");
while(read(fdes,&c,1)){printf("%c",c);}
printf("\n");


lseek(fdes,0,SEEK_SET);

//ret = 
read(fdes,rbuff,10);
if(ret < 0)printf("read() failed!!! ret=%d\n",ret);


printf("buff[0]=%c \n",buff[0]);
printf("rbuff[0]=%c \n",rbuff[0]);

system("cat myfile;rm myfile");
//system("cat;rm myfile");
}











int main()
{
myopen();



exit(0);
}



















