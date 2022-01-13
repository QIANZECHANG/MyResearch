#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

typedef struct N{
    int* p1;
    int* p2;
}node;

int func(int a){
    node x;
    x.p1=(int*)malloc(4);
    x.p2=(int*)malloc(4);
    free(*(&x.p1+1));
    //free(x.p1);
    //[+] { Insert: if (true) free(*(func:x.p2)) at 3 (line 16, column 5) }
    return 1;    
}
