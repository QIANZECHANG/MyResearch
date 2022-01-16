int func(int a){
  <#blue#node* tmp_o0;#>
  <#blue#node* tmp_o1;#>
  node *x=new_node(a);
  <#blue#tmp_o0 = x;#>
  x->next=new_node(a+1);
  tmp_o1 = x->next;
  <#orange#free(tmp_o1);#>
  <#orange#free(tmp_o0);#>
  return 0;
}
