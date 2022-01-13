#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    struct N *next;
    int v;
}node;


node *new_node(int a){
    node *n=(node*)malloc(sizeof(node));
    n->next=NULL;
    n->v=a;
    return n;
}


int func(int a){
    node *x=new_node(a);
    x->next=new_node(a+1);
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
