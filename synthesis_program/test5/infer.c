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


