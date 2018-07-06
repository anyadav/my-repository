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

void traverse(struct node* tree)
{
if(tree==(struct node*)NULL) return ;
else
{
printf("%d",tree->data);
traverse(tree->left);
traverse(tree->right);
}
}

int main()
{
struct node *root = (struct node*)NULL;

root=makenode(1);
root->left = makenode(2);
root->right = makenode(3);
root->left->left = makenode(4);

traverse(root);

printf("\n");
return(0);
}












