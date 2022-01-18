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

int LLVMFuzzerTestOneInput(char *data, int size) {
	    int n=0;
	        for(int i=0;i<size;i++){
			        if(! isdigit(*(data+i)))return 0;
				        n=n*10+ *(data+i)-'0';
					    }
		    func(n);
		        return 0;
}
