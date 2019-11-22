int main(){
    srand(1);
    int f[200];
    int t;


    for(int i=0;i<200;++i){
        f[i] = rand() % 12345;
    }

    printf("排序之前:\n");
    for(int i=0;i<200;++i){
        printf("%d ",f[i]);
    }

    for(int i=0;i<199;++i)
        for(int j=0;j<199;++j)
            if(f[j]> f[j+1]){
                t = f[j+1];
                f[j+1]=f[j];
                f[j]=t;
            }

    printf("\n\n排序之后:\n");
    for(int i=0;i<200;++i){
        printf("%d ",f[i]);
    }

    printf("\n");
    return 0;
}
