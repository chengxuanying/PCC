#define N 10

int swap(int a,int b){
    int t;
    t = *a;
    *a = *b;
    *b = t;
}

int main(){
    srand(1);
    int f[N];
    int t;

    for(int i=0;i<N;++i){
        f[i] = rand() % 12345;
    }

    printf("排序之前:\n");
    for(int i=0;i<N;++i){
        printf("%d ",f[i]);
    }

    for(int i=0;i<N-1;++i)
        for(int j=0;j<N-1;++j)
            if(f[j]> f[j+1])
                swap(&f[j+1],&f[j]);


    printf("\n\n排序之后:\n");
    for(int i=0;i<N;++i){
        printf("%d ",f[i]);
    }

    printf("\n");
    return 0;
}
