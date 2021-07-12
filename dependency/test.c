int test(char* data,int size){
  int a;
  int*b;
  int c=1;
  struct node *x;
  x->v=10+*data-'0';
  a=c+func(x->v,c);
  a=a+1;
  *b=a;
  a=0;
  c=a;
  return 0;
}

int func(int arg1,char* arg2){
  return arg1;
}