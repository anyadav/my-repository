#include<fcntl.h>
#include <sys/mman.h>

int main(int argc, char * argv[])
{




int fd;
void *filemap;
long filesize;

fd = open(argv[1],O_RDONLY)



