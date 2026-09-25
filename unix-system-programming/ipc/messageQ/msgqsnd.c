#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#include<sys/ipc.h>
#include<sys/msg.h>

struct msg_queue
{

long int mtype;
char name [20];
int tel;
};

char buff[20];
int type[20];

int main()
{

struct msg_queue mq;
int key,msqid,i=0;

key =ftok(".",'A');
if(key == -1){
perror("ftok");
exit(1);
}

msqid = msgget(key,IPC_CREAT|0666);
if(msqid == -1){
perror("msgget");
exit(1);
}

//Fill data to send
mq.mtype = 1;

printf("Enter some data to send: ");
if(fgets(buff, 20, stdin) == NULL){
perror("fgets");
exit(1);
}

mq.mtype = 1;
strcpy( mq.name, buff);

//mq.name ="AMAR NATH YADAV";
mq.tel = 9999;

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
*/


/* msgsz counts only the payload after mtype, not the whole struct */
msgsnd(msqid,&mq,sizeof(mq) - sizeof(long int),0);
printf("\n");
return 0;
}




