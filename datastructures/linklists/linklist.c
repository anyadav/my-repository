#include<stdlib.h>
#include<stdio.h>

#define NODESIZE sizeof(struct node)

struct node
{
  int data;
  struct node *next;
};

typedef struct node *NODE;


void insertend (NODE, int);
void printlist (NODE);
void insertpos (NODE, int pos, int val);
void insertmid (NODE, int);
void middlenode (NODE);
void introduceloop(NODE);
void detectloop(NODE);

void printNthFromLast(NODE head, int n); 


NODE deletelist (NODE);
NODE insertbeg (NODE, int);
NODE reverse (NODE);


int
main ()
{
  int i;
  NODE root = (NODE) 0;		//, root1;

  if (root = (NODE) malloc (NODESIZE))
    {
      root->next = NULL;
      root->data = 0;
    }


  for (i = 1; i < 10; i++)
    {
      insertend (root, i * 100);
    }

  root = insertbeg (root, 11);
  insertpos (root, 3, 30);
  insertmid (root, 1234);
  middlenode (root);


  printlist (root);
  root = reverse (root);
  printf ("\n Reverse of the list: \n==========================\n");
  printlist (root);

  printNthFromLast(root, 4); 
// root = deletelist (root);


introduceloop(root);
detectloop(root);  /*this function must be called after calling introduceloop() as to \
		   really get the result as introduceloop() introduces a loop in the \
		   link list */

  return 0;
}


void printNthFromLast(NODE head, int n) 
{
    static int i = 0;
    if (head == NULL)
       return;
    printNthFromLast(head->next, n);
    if (++i == n)
       printf("%dth node from Last: %d\n", n,head->data);
}






void detectloop(NODE head)
{
NODE fast,slow;
fast=slow=head;

while(slow->next && fast->next && fast->next->next)
{

slow=slow->next;
fast=fast->next->next;
if(slow==fast)
{
printf("Loop detected slow->data:[%d], fast->data:[%d] \n", slow->data, fast->data);
printf("Loop detected slow:[%u], fast:[%u] \n", slow, fast);
exit(0);
}

}}


void introduceloop(NODE head)
{
printf("introduced loop from [%d]->....[%d]\n",head->next->next->data, head->next->next->next->next->next->data);
head->next->next->next->next->next = head->next->next;
}


void
insertend (struct node *ptr, int val)
{
  if (ptr == NULL)
    {
      NODE root = (NODE) malloc (NODESIZE);
      root->next = NULL;
      root->data = val;
      printf ("no earlier list, this is first element you inserted \n");
      return;
    }

  NODE newnode = (NODE) malloc (NODESIZE);
  if (newnode == NULL)
    {
      printf ("unable to create node\n");
    }

  newnode->data = val;
  newnode->next = NULL;


  if (ptr->next == NULL)
    {
      ptr->next = newnode;
    }
  else
    {
      struct node *cur = ptr;
      while (1)
	{
	  if (cur->next == NULL)
	    {
	      cur->next = newnode;
	      break;
	    }
	  else
	    cur = cur->next;
	}
    }
}

void
printlist (struct node *ptr)
{
  if (ptr == (NODE) 0)
    {
      printf ("No list exists, head pointing to NULL \n");
      return;
    }

  while (ptr->next)
    {
      printf ("[%d]->", ptr->data);
      ptr = ptr->next;
    }
  printf ("[%d]\n", ptr->data);
}

void
insertpos (struct node *ptr, int pos, int val)
{
  NODE newnode = (NODE) malloc (NODESIZE);
  newnode->data = val;
  newnode->next = NULL;

  struct node *cur = ptr;

  while ((pos - 2))
    {

      if (ptr->next == NULL)
	{
	  printf ("list is smaller than position to be inserted\n");
	  exit (0);
	}
      else
	{
	  cur = cur->next;
	  pos--;
	}
    }
  newnode->next = cur->next;
  cur->next = newnode;

}




NODE
insertbeg (NODE ptr, int val)
{


  if (ptr == NULL)
    {
      ptr = (NODE) malloc (NODESIZE);
      ptr->next = NULL;
      ptr->data = val;
      printf ("no earlier list, this is first element you inserted \n");
      return (ptr);
    }


  NODE newnode = (NODE) malloc (NODESIZE);
  if (newnode == NULL)
    {
      printf ("node creation failed\n");
      exit (0);
    }
  newnode->data = val;
  newnode->next = NULL;

  newnode->next = ptr;
  ptr = newnode;

  return ptr;
}

void
insertmid (struct node *ptr, int val)
{
  NODE newnode = (NODE) malloc (NODESIZE);
  newnode->next = NULL;
  newnode->data = val;

  struct node *tptr;
  struct node *fptr;

  tptr = ptr;
  fptr = ptr;
  while (fptr->next != NULL)
    {
      if (fptr->next->next != NULL)
	{
	  fptr = fptr->next->next;
	  tptr = tptr->next;
	}
      else
	fptr = fptr->next;
    }

  newnode->next = tptr->next;
  tptr->next = newnode;
}



/* Reverse the link list */

NODE
reverse (NODE head)
{
  NODE revhead;
  if (head == NULL || head->next == NULL)
    {
      return (head);
    }


  revhead = reverse (head->next);
  head->next->next = head;
  head->next = NULL;
  return (revhead);

}

/*Print middle Node*/

void
middlenode (NODE head)
{
  NODE fast, slow;
  fast = slow = head;

  if (fast->next == NULL)
    printf ("Only one node\n");
  else if (fast->next->next == NULL)
    printf ("Just Tow nodes\n");
  else
    {
      while (fast->next != NULL && fast->next->next != NULL)
	{
	  fast = fast->next->next;
	  slow = slow->next;
	}

      printf ("Middle NOde is: [%d]\n", slow->data);
    }

}

/*Delete the Linked List */
NODE
deletelist (NODE head)
{
//NODE head = *ptr;
  if (head == NULL)
    return(head);
  deletelist (head->next);
//  head->next->next = (NODE) 0;
  free (head);
  return (head);
}
