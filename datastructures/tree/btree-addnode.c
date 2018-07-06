/* VERY BASIC PROGRAM of BINARY TREE */
#include<stdio.h>
#include<malloc.h>


//Declare node
struct node{

int data;
struct node *left;
struct node *right;
};


//Allocate new node

struct node* makenode(int data)
{
struct node* node = (struct node*)malloc(sizeof(struct node));

node->data = data;
node->left = NULL;
node->right = NULL;

return(node);
}


int main()
{
struct node *root = (struct node*)NULL;

root=makenode(1);
root->left = makenode(2);
root->right = makenode(3);
root->left->left = makenode(4);

return(0);
}












