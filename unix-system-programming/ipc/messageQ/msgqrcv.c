//#include<stdlib.h>
#include<stdio.h>
//#include<string.h>
//#include<errno.h>
//#include<unistd.h>


//#include<sys/types.h>
#include<sys/ipc.h>
#include<sys/msg.h>


/*THIS PROGRAM NEEDS TO BE COMPLTED, JUST COPIED THE SEND*/

struct msg_queue
{

long int mtype;
char name [20];
int tel;
};

int type[20];

int main()
{

long int msg_to_rcv = 1;
struct msg_queue mq;
int key,msgid,i=0;

key =ftok(".",'A');

msgid = msgget(key,IPC_CREAT|0666);


msgrcv(msgid, (void *)&mq, BUFSIZ, msg_to_rcv,0);
printf("You wrote:  %s\n",mq.name);

msgctl(msgid,IPC_RMID,0);



/*
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
*/

return 0;
}




