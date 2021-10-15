struct M{int* p1; int* p2;};
void func(int a, int b){
    struct M m;
    m.p1=(int*)malloc(4);
    m.p2=(int*)malloc(4);
    int c=a+b;
    int* n;
    if(c>5)
        n=m.p1;
    else
        n=malloc(4);
    free(*(&m.p1 + 1));
    free(n);
}

