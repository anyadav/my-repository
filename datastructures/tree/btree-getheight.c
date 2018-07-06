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


/* GET HEIGHT OF THE BINARY TREE*/

int getheight(struct node* tree)
{
if(tree == NULL)
{ return 0 ;}
else{
int lheight=getheight(tree->left);
int rheight=getheight(tree->right);

if(lheight > rheight)
	return (lheight+1);  //here +1 takes care of increaing and ultimately getting the height
else 
	return (rheight+1); //here +1 takes care of increaing and ultimately getting the height

}
}


int main()
{

int height;
struct node *root = (struct node*)NULL;

root=makenode(1);
root->left = makenode(2);
root->right = makenode(3);
root->left->left = makenode(4);

height=getheight(root);
printf("Height of tree is: %d\n",height);

return(0);
}












