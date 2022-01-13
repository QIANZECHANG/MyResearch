#include <stdlib.h>
#include <ctype.h>
#include <stdio.h>

int func(int a){
    int *p=malloc(4);
    int *b=&a;
    if(a<5){
        return 0;
    }
    *p=1;
    return 1;    
}
