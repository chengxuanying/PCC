int swap(int a,int b){
    int t;
    t = *a;
    *a = *b;
    *b = t;
}

int main(){
    srand(1);
    int f[20];
    int t;

    for(int i=0;i<20;++i){
        f[i] = rand() % 12345;
    }

    printf("排序之前:\n");
    for(int i=0;i<20;++i){
        printf("%d ",f[i]);
    }

    for(int i=0;i<19;++i)
        for(int j=0;j<19;++j)
            if(f[j]> f[j+1])
                swap(&f[j+1],&f[j]);


    printf("\n\n排序之后:\n");
    for(int i=0;i<20;++i){
        printf("%d ",f[i]);
    }

    printf("\n");
    return 0;
}
