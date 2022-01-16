int func(int a){
  <#blue#field* tmp_o0;#>
  <#blue#node* tmp_o1;#>
  <#green#int tmp_a = a;#>
  <#blue#node* tmp_o2;#>
  <#blue#field* tmp_o3;#>
  node *x=new_node(a);
  <#blue#tmp_o0 = x->m;tmp_o2 = x;#>
  node *y=new_node(a);
  <#blue#tmp_o1 = y;tmp_o3 = y->m;#>
  x->v=a;
  x->m->k=a+1;
  y->v=a;
  y->m->k=a+1;
  if(a<5){
    free(x);
  }
  <#orange#free(tmp_o3);#>
  <#orange#if(tmp_a>=5)free(tmp_o2);#>
  <#orange#free(tmp_o1);#>
  <#orange#free(tmp_o0);#>
  return 0;
}




