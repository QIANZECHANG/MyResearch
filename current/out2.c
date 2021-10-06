int test(char *data, int size)
{
  int *p;
  int *q;
  int num = 0;
  for (int i = 0; i < size; i++)
  {
    if (!isdigit(*(data + i)))
      return 0;

    num = ((num * 10) + (*(data + i))) - '0';
  }

  p = malloc(4);
  if (num < 5)
    q = p;
  else
  {
    q = malloc(4);
  }

  *q = 1;
  free(q);
  if (num >= 5)
    free(p);

  return 0;
}

int LLVMFuzzerTestOneInput(char *data, int size)
{
  test(data, size);
  return 0;
}

