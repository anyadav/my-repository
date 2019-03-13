#include<stdio.h>
#define MAX 10
char* getReverse(char[]);

int main(){

    char str[MAX],*rev;

    printf("\nEnter  any string: ");
    scanf("%s",str);
    printf("You Entered: %s\n",str);
    rev = getReverse(str);

    printf("Reversed string is: %s\n\n",rev);
    return 0;
}    

char* getReverse(char str[]){

    static int i=0;
    //int i=0;
    //static char rev[MAX];
    char rev[MAX];

    if(*str){
         getReverse(str+1);
         rev[i++] = *str;
    }

    return rev;
}
