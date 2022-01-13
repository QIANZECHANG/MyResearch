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


int func(int a){node* tmp_o0;node* tmp_o1;
    node *x=new_node(a);tmp_o0 = x;
    x->next=new_node(a+1);tmp_o1 = x->next;
    free(tmp_o1);free(tmp_o0);return 0;
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
