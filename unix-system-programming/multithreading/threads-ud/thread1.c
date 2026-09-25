#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
#include<pthread.h>

/* This file was previously an incomplete fragment: it referenced an
 * undeclared "count" (the declared variable was "count1") and an
 * undeclared "run_now", was missing <stdio.h>/<unistd.h>, had a stray
 * ";" after "sleep(1)" inside the else block, and had no main() to
 * actually run it. Fixed into a complete, standalone, compilable demo. */

int run_now = 1;

void *thrfun1(void *arg)
{
int count1=0;

while (count1++<20){
	if(run_now ==1){
		printf("1");
		run_now =2;
		}
	else{sleep(1);}
	}
return NULL;
}

int main(void)
{
pthread_t t1;
int res = pthread_create(&t1, NULL, thrfun1, NULL);
if(res != 0){
perror("pthread_create");
exit(EXIT_FAILURE);
}
pthread_join(t1, NULL);
printf("\n");
return 0;
}
