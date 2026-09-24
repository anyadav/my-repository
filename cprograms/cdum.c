#include<stdio.h>
#include<stdlib.h>

int dif(int i, int j){
	if(i>=j) return (i-j);
	else return (j-i);
}
int mul(int i, int j){return i*j;}

int add(int i, int j){ 
char *pt;
printf("add: %d\n",(i+j));

printf("mul: %d\n",mul(i,j));
printf("dif : %d\n",dif(i,j));
pt = "amar";
printf("%s \n",(char *)pt);
pt++;
return (i+j);
}


int main(){


int a=2;
int b=3;
int c=4;
int d=5; 
int ad,di,mu;
int *pt;

pt = (int *)malloc(sizeof(int));
if(pt == NULL)
	return 1;
*pt = a;

ad = add(*pt,b);
di = dif(d,c);
mu =mul(ad,di);
printf("mul(add,dif): %d\n",mu);

free(pt);
return 0;

}
