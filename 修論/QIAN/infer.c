int* alloc(){
  int* p=malloc(sizeof(int));
  return p;
}

void foo(){
  int* p=alloc();
}