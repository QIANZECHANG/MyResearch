#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    struct M *m;
    int v;
}node;

typedef struct M{
    struct M *next;    
    int k;
}field;

node *new_node(int a){
    node *n=(node*)malloc(sizeof(node));
    n->m=(field*)malloc(sizeof(field));
    n->m->next=NULL;
    return n;
}

int func(int a){int tmp_a = a;
    node *x=new_node(a);node* tmp_o0 = x;field* tmp_o1 = x->m;
    x->v=a;
    x->m->k=a+1;
    if(a<5){
        free(x);
    }
    free(tmp_o1);if(tmp_a>=5)free(tmp_o0);return 0;    
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