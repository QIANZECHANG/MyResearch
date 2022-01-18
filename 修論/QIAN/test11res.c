int func(int a){
  <#green#int tmp_a = a;#>
  <#blue#int* tmp_o0;#>
  int *p=f();
  <#blue#tmp_o0 = p;#>
  if(a>5){
    g(p);
  }
  <#orange#if(tmp_a<=5)free(tmp_o0);#>
  return 0;
}