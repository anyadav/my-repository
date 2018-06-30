#include<sys/ipc.h>
#include<sys/msg.h>

/*THIS PROGRAM NEEDS TO BE COMPLTED, JUST COPIED THE SEND*/

struct msg_queue
{

long mtype;
char name [20];
int tel;
};

int type[20];

int main()
{

struct msg_queue mq;
int key,msqid,i=0;

key =ftok(".",'A');

msgget(key,IPC_CREAT|0666);

while(1)
{
printf("Enter the mtype :");
scanf("%d\n",&mq.mtype);
type[i++]=mq.mtype;
printf("Enter Name :");
scanf("%s\n",&(mq.name));
printf("Enter Tel :");
scanf("%d\n",&(mq.tel));

msgsnd(msqid,&mq,sizeof(mq),0);
printf("\n");
}
return 0;
}




