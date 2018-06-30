struct node
{

int data;
struct node *next;
};

void insertend(struct node *ptr, int val);
void traverselist(struct node *ptr);
void insertpos(struct node *ptr, int pos, int val);
struct node *insertbeg(struct node *ptr, int val);
void insertmid(struct node *ptr, int val);
