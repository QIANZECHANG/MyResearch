#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    int* p1;
    int* p2;
}node;

int func(int a){
    node x;
    x.p1=(int*)malloc(4);
    x.p2=(int*)malloc(4);
    int* n;
    if(a<5){
        n=x.p1;
    }else{
        n=malloc(4);
    }
    free(*(&x.p1+1));
    free(n);
    return 1;    
}
