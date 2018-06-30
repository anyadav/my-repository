#include <stdio.h>

int main(int argc, char *argv[])
{
    int numbers[4] = {0}; //initializing by single entry will initialize all elements by zero - expected 
    char name[4] = {'a'};//initialize only 1st entry to 'a' remaining to 0 for char array

    
/*showing all entryies are initialized by zero */
    printf("numbers: %d %d %d %d\n", numbers[0], numbers[1], numbers[2], numbers[3]);


/*showing 1st eentry is initialized by 'a', remaining are initialized by 0*/
    printf("name each: %c %c %c %c\n", name[0], name[1], name[2], name[3]);
    printf("name each: %c %d %d %d\n", name[0], name[1], name[2], name[3]);



/*printing full array as string */
    printf("name: %s\n", name);

/*set indivisual entries */
    numbers[0] = 1;
    numbers[1] = 2;
    numbers[2] = 3;
    numbers[3] = 4;

/*set indivisual entries */
    name[0] = 'Z';
    name[1] = 'e';
    name[2] = 'd';
    name[3] = '\0';

/*print array after initializing */
    printf("numbers: %d %d %d %d\n", numbers[0], numbers[1], numbers[2], numbers[3]);
    printf("name each: %c %c %c %c\n", name[0], name[1], name[2], name[3]);


/*print array as string */
    printf("name: %s\n", name);


/* initialize pointer by string and print it as array, shows string and char arrays are same*/
    char *another = "Zed";

    printf("another: %s\n", another);
    printf("another each: %c %c %c %c\n", another[0], another[1], another[2], another[3]);

    return 0;
}
