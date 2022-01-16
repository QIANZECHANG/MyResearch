int func(int a){
  node *x=new_node(a);
  node *y=new_node(a);
  x->v=a;
  x->m->k=a+1;
  y->v=a;
  y->m->k=a+1;
  if(a<5){
    free(x);
  }
  return 0; 
}




