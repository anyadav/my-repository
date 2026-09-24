#include<fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char * argv[])
{




int fd;
void *filemap;
long filesize;
struct stat sb;

if(argc != 2)
{
fprintf(stderr, "Usage: %s <file>\n", argv[0]);
return 1;
}

fd = open(argv[1],O_RDONLY);
if(fd < 0)
{
perror("open");
return 1;
}

if(fstat(fd, &sb) < 0)
{
perror("fstat");
close(fd);
return 1;
}
filesize = sb.st_size;

if(filesize == 0) /* mmap of length 0 fails, nothing to print */
{
close(fd);
return 0;
}

filemap = mmap(NULL, filesize, PROT_READ, MAP_PRIVATE, fd, 0);
if(filemap == MAP_FAILED)
{
perror("mmap");
close(fd);
return 1;
}

/* print the mapped file contents */
fwrite(filemap, 1, filesize, stdout);

munmap(filemap, filesize);
close(fd);
return 0;
}
