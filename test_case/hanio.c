

int hanio(int a,int b, int c,int n)
{
    if( n==1 )	{printf("%c->%c\n",a,c);}
    else{
        hanio(a,c,b,n-1);
        printf("%c->%c\n",a,c);
        hanio(b,a,c,n-1);
    }
}

int main() {

    hanio('A','B','C',3);
    return 0;
}