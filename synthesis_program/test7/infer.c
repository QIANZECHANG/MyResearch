#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int func(int a){
    int *p=malloc(4);
    if(a>5){
      *p=a;
      free(p);
      return 0;
    }else{
      //*p=a;
      return 1;
    }   
}
