#include<stdio.h>

#define ROW 10
#define COL 15

int main(){
int i,j;
int array[ROW][COL];

for(i = 0; i < ROW;i++)
{
for (j = 0; j < COL;j++)

array[i][j]= (i+1)*(j+1);

}

for(i=0;i<ROW; i++){
for(j=0;j<COL; j++)
printf("%d\t",array[i][j]);

printf("\n");
}
}
