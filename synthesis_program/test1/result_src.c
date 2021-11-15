#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int func(int a){
    int *p=malloc(4);int* tmp_o0 = p;
    int *b=&a;
    if(a<5){
        //free(p);
        free(tmp_o0);return 0;
    }
    free(tmp_o0);return 1;    
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