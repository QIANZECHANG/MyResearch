#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    struct N *next;
}node;

node *new_node(){
    node *n=(node*)malloc(sizeof(node));
    n->next=NULL;
    return n;
}


int func(int a){int tmp_a = a;
    node *x=new_node();node* tmp_x = x;
    if(a<5){
        free(x);
        if(tmp_a>=5)free(tmp_x);return 0;
    }
    if(tmp_a>=5)free(tmp_x);return 1;    
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