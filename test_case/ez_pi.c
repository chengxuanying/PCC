int main(){
  int a = 10000;
  int b = 0;
  int c=2800;
  int d = 0;
  int e = 0;
  int f[2801];
  int g = 0;

  for(; b<c ;) {
    f[b]=a/5;
    ++b;
  }
  for(; c*2; ){
    d=0;
    g=c*2;
    for(b=c;; ){
        d+=f[b]*a;
        --g;f[b]=d%g;
        d/=g;--g;
        --b;
        if(b==0)break;

        d*=b;

    }
    c-=14;
    printf("%.4d",e+d/a);
    e = d%a;
  }

  printf("\n");
  return 0;
}