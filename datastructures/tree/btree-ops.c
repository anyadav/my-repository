#include<stdio.h>
#include<malloc.h>

//Declare node
struct node{

int data;
struct node *left;
struct node *right;

};


/* ALL PROTOTYPES */
struct node* makenode(int data);
int getheight(struct node* tree);
void traverse(struct node* tree);



int main()
{
int height;

struct node *tree=(struct node*)NULL;
tree=makenode(10);

tree->left = makenode(8);
tree->right = makenode(20);

tree->left->left = makenode(5);
tree->left->right = makenode(9);

tree->right->left = makenode(15);
tree->right->right = makenode(25);

height = getheight(tree);
printf("Height of tree: %d\n",height);

traverse(tree);
printf("\n");

return 0;
}





//CREATE NODE
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




void traverse(struct node* tree)
{
if(tree==(struct node*)NULL) return ;
else
{
printf("%d  ",tree->data);
traverse(tree->left);
traverse(tree->right);
}
}



