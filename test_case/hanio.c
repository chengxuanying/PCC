
int cnt = 0;
int hanio(int a,int b, int c,int n)
{
    if( n==1 )	{printf("%c->%c\n",a,c); cnt +=1;}
    else{
        hanio(a,c,b,n-1);
        printf("%c->%c\n",a,c);
        cnt +=1;
        hanio(b,a,c,n-1);
    }
}

int main() {
    for(int i = 1;i<=3;++i){
        printf("当i=%d时\n",i);
        cnt = 0;
        hanio('A','B','C',i);
        printf("%d\n\n",cnt);
    }
    return 0;
}

