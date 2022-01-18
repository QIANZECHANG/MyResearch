int func(int a){
  int *p=f();
  <#orange#free(p);#>
  if(a>5){
    g(p);
  }	
  return 0;
}

