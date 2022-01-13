#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    int* p1;
    int* p2;
}node;

int func(int a){int* tmp_o0;int tmp_a = a;int* tmp_o1;
    node x;
    x.p1=(int*)malloc(4);tmp_o0 = x.p1;
    int* n;
    if(a<5){
        n=x.p1;
    }else{
        n=malloc(4);tmp_o1 = n;
    }
    if(tmp_a>=5)free(tmp_o1);free(tmp_o0);return 1;
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
