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
void printnodeatlevel(struct node* tree,int level);
struct node* insertinbinarytree(struct node*, int);

int main()
{
int height,level;

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

printf("All the node data of tree:   ");
traverse(tree);
printf("\n");

for(level=1;level<=height;level++)
{
printf("node data at level %d:  ",level);
printnodeatlevel(tree,level);
printf("\n");
}


return 0;
}

/*   **********UNDER PROGRESS***************
 *
 *   Fucntion: insertinbinarytree
 *   Description: This function takes two parameter a input
 *   -pointer to root node of tree
 *   -Data to be inserted(here we are dealing with int data as of now
 */   
struct node* insertinbinarytree(struct node* tree, int data)
{
struct node* temp =tree;
if(temp==(struct node*)NULL)
{
temp->data=data;
temp->left=(struct node*)NULL;
temp->right=(struct node*)NULL;

return tree;
}
else if(temp->left == (struct node*)NULL)
{
temp->left->data=data;
temp->left->left=(struct node*)NULL;
temp->left->right=(struct node*)NULL;
return tree;
}

}



/*The function: printnodeatlevel prints the node data at a perticular level.
 * Input: take two input:
 * -pointer to root node of tree
 * -level, an integer value 
 *Output: prints all the node data at level provided in input. 
 * This is basically the breadth first traversal if you print for all the level
 *  */
void printnodeatlevel(struct node* tree, int level)
{
if(tree == NULL) return;
else if(level ==1)
printf("%d  ",tree->data);
else
{
printnodeatlevel(tree->left,level-1);
printnodeatlevel(tree->right,level-1);

}
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



/*TRAVERSE AND PRINT ALL THE NODES DATA OF TREE */
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



