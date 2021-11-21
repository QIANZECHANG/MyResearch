#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int func(int a){
    int *p=malloc(4);
    int *q;
    if(a<5){
        q=p;
    }else{
        q=malloc(4);
    }
    *p=1;
    free(q);
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