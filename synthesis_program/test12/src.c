#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int func(int a){
    int **x;
    x = (int**)malloc(sizeof(int*)*2);
    x[0] = (int*)malloc(sizeof(int));
    x[1] = (int*)malloc(sizeof(int));
    int b=0;
    free(*x);
    free(*(x+1));
    free(x);
    return 1;    
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