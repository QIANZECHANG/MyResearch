int test(int data,char* str){
  int a;
  int*b;
  int c=1;
  struct node *x;
  x->v=data;
  a=c+func(x->v,c);
  a=a+1;
  *b=a;
  return 0;
}

int func(int arg1,char* arg2){
  return arg1;
}