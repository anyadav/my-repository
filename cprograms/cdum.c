#include<stdio.h>

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
printf("%s \n",(char *)pt);
pt = "amar";
pt++;
return (i+j);
}


int main(){


int a=2;
int b=3;
int c=4;
int d=5; 
int ad,di,mu;
char *ptr;
int *pt;

pt = (int *)malloc(sizeof(int));
pt =&a;

ad = add(a,b);
//di = dif(d,c);
//mu =mul(ad,di);

free(pt);
return 0;

}
