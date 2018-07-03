//#include<stdlib.c>
#include<stdio.h>
#include "amar.h"

int main()
{
struct node *root,root1;
root=(struct node *)malloc(sizeof(struct node));

root->next = NULL;
root->data = 1;

insertend(root,2);
insertend(root,3);
insertend(root,4);
insertend(root,5);
root = insertbeg(root,11);
insertpos(root,3,30);
insertpos(root,3,30);

insertpos(root,3,30);
insertend(root,3);
insertpos(root,3,300);
insertend(root,3);

insertpos(root,4,40);
insertpos(root,7,70);
insertend(root,3);
//insertpos(root,6,60);
insertpos(root,8,80);
insertpos(root,10,100);


traverselist(root);

insertmid(root,1234);

traverselist(root);
return 0;

}


void insertend(struct node *ptr, int val)
{

struct node *newnode = (struct node *)malloc(sizeof(struct node));
if(newnode ==NULL)
{
printf("unable to create node\n");
}

newnode->data = val;
newnode->next = NULL;


if(ptr->next ==NULL){
ptr->next = newnode;	
}
else{
struct node *cur= ptr;
while(1)
{
if(cur->next ==NULL){
cur->next =newnode;
break;
}
else
cur = cur->next;
}
}
}

void traverselist(struct node *ptr){
while(ptr->next){
printf("%d, ",ptr->data);
ptr = ptr->next;
}
printf("%d\n",ptr->data);
}

void insertpos(struct node *ptr, int pos, int val){
struct node *newnode = (struct node *)malloc(sizeof(struct node));
newnode->data = val;
newnode->next = NULL;

struct node *cur = ptr;

while((pos-2))
{

if(ptr->next == NULL){
printf("list is smaller than position to be inserted\n");
exit(0);
}
else{
cur = cur->next;
pos--;
}
}
newnode->next=cur->next;
cur->next = newnode;

}




struct node *insertbeg(struct node *ptr, int val){
struct node *newnode = (struct node *)malloc(sizeof(struct node));
if(newnode ==NULL)
{
printf("node creation failed\n");
exit(0);
}
newnode->data = val;
newnode->next =NULL;

//struct node *tmp;
//tmp =ptr;

newnode->next = ptr;
ptr = newnode;

return ptr;
}

//struct node * insertmid(struct node *ptr, int val)
void insertmid(struct node *ptr, int val)
{
struct node *newnode = (struct node*)malloc(sizeof(struct node));
newnode->next = NULL;
newnode->data = val;

struct node *tptr;
struct node *fptr;

tptr = ptr;
fptr =ptr;
while(fptr->next!=NULL)
{
if(fptr->next->next!=NULL){
  fptr = fptr->next->next;
  tptr = tptr->next;
}
else
  fptr = fptr->next;
}

/*
while(fptr->next->next!=NULL)
{
  fptr = fptr->next->next;
  tptr = tptr->next;
}
*/
newnode->next = tptr->next;
tptr->next=newnode;
//return ptr;
}






