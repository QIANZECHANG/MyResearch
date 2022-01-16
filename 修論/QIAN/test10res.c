int func(int a){
  <#blue#int* tmp_o0;#>
  <#green#int tmp_a = a;#>
  <#blue#int* tmp_o1;#>
  node x;
  x.p1=(int*)malloc(4);
  <#blue#tmp_o0 = x.p1;#>
  int* n;
  if(a<5){
    n=x.p1;
  }else{
    n=malloc(4);
    <#blue#tmp_o1 = n;#>
  }
  <#orange#if(tmp_a>=5)free(tmp_o1);#>
  <#orange#free(tmp_o0);#>
  return 1;
}

