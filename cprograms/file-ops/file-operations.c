#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>

/*Example program to use basic system calls related to file e.g. open(), read(),write(),lseek() */
void
myopen ()
{
  int ret, i = 0;
  char c;
  char buff[20] =
    { 'a', 'm', 'a', 'r', ' ', 'n', 'a', 't', 'h', ' ', 'y', 'a', 'd', 'a',
'v' };
  char rbuff[20];


  int fdes;
  fdes = open ("myfile", O_RDWR | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);
  if (fdes < 0)
    {
      perror ("open myfile");
      return;
    }

  ret = write (fdes, buff, 15);
  if (ret < 0)
    printf ("write() failed!!!ret = %d\n", ret);

  system ("echo myfile data;cat myfile");


  lseek (fdes, 0, SEEK_SET);
  printf ("data written by write() into myfile from buff\n");
  while (read (fdes, &c, 1) > 0)
    {
      printf ("%c", c);
    }
  printf ("\n");


  lseek (fdes, 0, SEEK_SET);

  ret = read (fdes, rbuff, 10);
  if (ret < 0)
    printf ("read() failed!!! ret=%d\n", ret);

  while (i < ret)
    {
      printf ("rbuff[%d]=%c \n", i, rbuff[i]);
      i++;
    }

  close (fdes);
  system ("cat myfile;#rm myfile");
}





/* ********************* copyfile() *****************************/
/* This function copies the one file to other file,
Program will basically read the input-file char by char and copy the data 
to outputfile byte by byte */


void
copyfile ()
{

  int in, out;
  char c;

  in = open ("file-operations.c", O_RDONLY);
  out = open ("output-file", O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);
  if (in < 0 || out < 0)
    {
      perror ("copyfile open");
      if (in >= 0)
        close (in);
      if (out >= 0)
        close (out);
      return;
    }

  while (read (in, &c, 1) > 0)
    write (out, &c, 1);

  close (in);
  close (out);

}





/******************************** copyfileinchunks() *********************/
/* 
This function copies any files to other file in chunks of 1kb(1024 bytes)
Also, if in the input file you pass the name of this file which consist this program, 
this program will take care to copy the complete lines in the copied-file. Same thing can be achieved 
by above function copyfile() as well
*/


void
copyfileinchunks ()
{

  char buff[1024];
  int in, out, nread;

  in = open ("file-operations.c", O_RDONLY);
  out = open ("copied-file", O_WRONLY | O_CREAT | O_TRUNC, S_IRUSR | S_IWUSR);
  if (in < 0 || out < 0)
    {
      perror ("copyfileinchunks open");
      if (in >= 0)
        close (in);
      if (out >= 0)
        close (out);
      return;
    }

  while ((nread = read (in, buff, sizeof (buff))) > 0)
    write (out, buff, nread);

  close (in);
  close (out);
}
































int
main ()
{
  myopen ();
  copyfile ();
  copyfileinchunks ();

  exit (0);
}
