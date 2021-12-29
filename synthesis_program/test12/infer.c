#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int func(int a){
    int **x;
    x = (int**)malloc(sizeof(int*)*2);
    x[0] = (int*)malloc(sizeof(int));
    x[1] = (int*)malloc(sizeof(int));
    free(*x);
    free(*(x+1));
    free(x);
    return 1;    
}

