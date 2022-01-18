#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int* f(){
  int *a=(int*)malloc(sizeof(int));
  return a;
}

void g(int*p){
  *p=1;
  free(p);
}

int func(int a){
  int *p=f();
  if(a>5){
    g(p);
  }	
  return 0;
}

