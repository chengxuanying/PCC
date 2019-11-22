int swap(int a,int b){
    int t;
    t = *a;
    *a = *b;
    *b = t;
}

int main(){
  int a = 123;
  int b = 321;

  printf("%ld,%ld\n",a,b);
  swap(&a,&b);
  printf("%ld,%ld\n",a,b);
}
