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

int func(int a){
  node *x=new_node(a);//o0, o2
  node *y=new_node(a);//o1, o3
  x->v=a;
  x->m->k=a+1;
  y->v=a;
  y->m->k=a+1;
  if(a<5){
    free(x);
  }
  return 0;    
}