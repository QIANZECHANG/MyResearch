#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    int v;
}node;

node *new_node1(int a){
    node *n=(node*)malloc(sizeof(node));
    n->v=a;
    return n;
}

node *new_node2(int a){
    node *n=(node*)malloc(sizeof(node));
    n->v=a*a;
    return n;
}

int func(int a){
    node* (*p[])()={new_node1,new_node2};
    node *x;
    node *y=malloc(sizeof(node));
    x=(*p[0])(a); 
    if(a<5){
        x=(*p[1])(a);
    }
    x->v=10;
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