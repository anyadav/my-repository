#include<stdio.h>
#include<string.h>

#define MAX 256

/* Reverse the order of words in a line, but not the letters of each word.
   e.g. "hello big world" -> "world big hello" */
void reverseWords(char *line)
{
    int end = strlen(line);
    int start, first = 1;

    while (end > 0) {
        while (end > 0 && line[end - 1] == ' ')   /* skip trailing spaces */
            end--;
        start = end;
        while (start > 0 && line[start - 1] != ' ') /* find start of word */
            start--;
        if (start < end) {
            if (!first)
                printf(" ");
            printf("%.*s", end - start, line + start);
            first = 0;
        }
        end = start;
    }
    printf("\n");
}

int main(){

    char line[MAX];

    printf("Enter a line: ");
    if (fgets(line, sizeof(line), stdin) == NULL)
        return 1;
    line[strcspn(line, "\n")] = '\0';

    reverseWords(line);
    return 0;
}
