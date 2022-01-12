typedef struct N{
  int v;
}node;

node *new_node1(int a){
  node *n=(node*)malloc(sizeof(node));
  n->v=a;
  return n;
}

node *new_node2(int a){
  node *n=(node*)malloc(sizeof(node));
  n->v=a*a;
  return n;
}

int func(int a){
  <#blue#node* tmp_o0;#>
  <#blue#node* tmp_o2;#>
  <#green#int tmp_a = a;#>
  <#blue#node* tmp_o1;#>
  node* (*p[])()={new_node1,new_node2};
  node *x;
  node *y=(node*)malloc(sizeof(node));
  <#blue#tmp_o2 = y;#>
  x=(*p[0])(a);
  <#blue#tmp_o0 = x;#>
  if(a<5){
    x=(*p[1])(a);
    <#blue#tmp_o1 = x;#>
  }
  x->v=10;
  <#orange#if(tmp_a<=4)free(tmp_o1);#>
  <#orange#free(tmp_o2);#>
  <#orange#free(tmp_o0);#>
  return 0;
}
