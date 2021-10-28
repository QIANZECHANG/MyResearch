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
    if (num >= 5)
      free(p);

    q = malloc(4);
  }

  *q = 1;
  free(q);
  return 0;
}

int LLVMFuzzerTestOneInput(char *data, int size)
{
  test(data, size);
  return 0;
}


int test1(int a, int* b){
  while(a<10 && *b >10){
      int c=a;
      break;
  }
}
