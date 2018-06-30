#include<stdio.h>
#include<stdlib.h>

#define ROW 3
#define COL 5

int main()
{

int i, j, count=0;



printf("\nPRINTING ARRAY USING METHOD ONE\n");
/* first way is to simply allocate memory enough for row*col and use it 
 * that is using a single pointer */

int *arr = (int *)malloc(ROW*COL*sizeof(int));


/*fill the allocated array */

for (i = 0; i < ROW; i++){
for (j = 0; j < COL; j++)
	{*(arr + i*COL + j) = ++count;}
}


/* print the array */

for (i = 0; i < ROW; i++){
for (j = 0; j < COL; j++)
{ printf("%d\t",*(arr + i*COL + j));}
printf("\n");
}

/*END OF FIRST METHOD */
printf("\nEND OF FIRST METHOD, PRINTING ARRAY USING SECOND METHOD NOW\n");

/*SECOND METHOD STARTS HERE*/

/*using array of pointers:
 * We can create an array of pointers of size r. 
 * Note that from C99, C language allows variable sized arrays. 
 * After creating an array of pointers, we can dynamically 
 * allocate memory for every row.
 */


/*
 * please note, as arr is already declared above,
 * so you have to take other name else error will come
 * */

/* decalare array of integer pointers */
int *arr1[ROW];

for(i = 0; i< ROW; i++){
arr1[i] = (int *)malloc(COL*sizeof(int)); //for all int pointers in array allocate memory of size col*int_size
}

count = 0;

/*fill the array */
for (i = 0; i < ROW; i++)
for (j = 0; j < COL; j++)
	arr1[i][j] = ++count;  // or you can use *(*(arr1+i)+j) = ++count

/*print the array */
for (i = 0; i < ROW; i++){
for (j = 0; j < COL; j++)
	printf("%d\t",*(*(arr1+i)+j));
printf("\n");
}




/*END OF SECOND METHOD */

printf("\nEND OF SECON METHOD, PRINTING ARRAY USING THIRD METHOD NOW\n");

/*THIRD METHOD STARTS HERE*/

/* Using pointer to a pointer:
 * We can create an array of pointers also dynamically using a double pointer. 
 * Once we have an array pointers allocated dynamically, 
 * we can dynamically allocate memory and for every row like method 2.
 */

int **arr2 = (int **)malloc(ROW*sizeof(int));
for( i = 0; i < ROW; i++)
 arr2[i] = (int *)malloc(COL*sizeof(int));

count = 0;

/*fill the array */
for (i = 0; i < ROW; i++)
for (j = 0; j < COL; j++)
        arr2[i][j] = ++count;  // or you can use *(*(arr1+i)+j) = ++count


/*print the array */
for (i = 0; i < ROW; i++){
for (j = 0; j < COL; j++)
        printf("%d\t",*(*(arr2+i)+j));
printf("\n");
}


/*THIRD METHOD ENDS HERE*/

printf("\nPRINTING ARRAY ELEMENTS DIFFERENT WAYS\n");
for (i = 0; i < ROW; i++){
  for (j = 0; j < COL; j++)
	printf("%d %d %d\t",arr2[i][j],*(arr2[i]+j),*(*(arr2+i)+j));
printf("\n");
}






return 0;
} /*end of main */
