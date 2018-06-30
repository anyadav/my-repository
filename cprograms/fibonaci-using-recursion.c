int
fibon (int n)
{
  if (n == 1 || n == 2)
    return 1;

  else
    return (fibon (n - 1) + fibon (n - 2));
}

int
main ()
{
  int n = 10;
  int i;
  for (i = 1; i <= n; i++)
    {
      printf ("%d\t", fibon (i));
    }
  return 0;

}
