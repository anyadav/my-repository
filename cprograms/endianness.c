int
main ()
{
  int var;
  char *ptr;
  var = 0x76543210;
  ptr = (char *) &var;
  printf ("ptr is: 0x%x\n", *ptr);
  printf ("ptr is: %x\n", *(ptr + 1));
  printf ("ptr is: %x\n", *(ptr + 2));
  printf ("ptr is: 0x%x\n", *(ptr + 3));
  if (*ptr == 0x10)
    printf ("litle endian");

  else
    printf ("Big endian");
  return 0;
}
