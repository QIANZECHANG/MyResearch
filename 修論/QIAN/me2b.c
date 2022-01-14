typedef struct N{
  int* p1;
  int* p2;
}node;

int func(int a){
  node x;
  x.p1=(int*)malloc(4);//o0
  x.p2=(int*)malloc(4);//o1
  free(*(&x.p1+1));
  free(x.p1);
  <#orange#free(x.p2);#>
  return 1;    
}
