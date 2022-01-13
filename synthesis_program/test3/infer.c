#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    struct M *m;
    int v;
}node;

typedef struct M{
    struct M *next;    
}field;

node *new_node(int a){
    node *n=(node*)malloc(sizeof(node));
    n->m=(field*)malloc(sizeof(field));
    n->m->next=NULL;
    n->v=a;
    return n;
}


node *bar(int a){
    node *x=new_node(a);
    return x;    
}

int foo(int a){
    node *x=bar(a);
    x->v=1;
    return 0;
}


