int func(int a){
  node x;
  x.p1=(int*)malloc(4);
  int* n;
  if(a<5){
    n=x.p1;
  }else{
    n=malloc(4);
  }
  <#orange#free(x.p1);#>
  <#orange#free(n);#>
  return 1;    
}
