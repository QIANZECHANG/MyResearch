typedef struct _p11_dict {
    struct p11_dictbucket **buckets;
}p11_dict;

typedef struct p11_dictbucket {
    struct p11_dictbucket *next;
} dictbucket;


int num=0;
p11_dict *p1_1;
dictbucket **p1_2;
dictbucket **p2_1;
int c1_1;
int c2_1;

p11_dict *
p11_dict_new (){
    p11_dict *dict;
    dict = malloc (sizeof (p11_dict));
    if(num==1)p1_1=dict;
    if (dict) {
        dict->buckets.aa = (dictbucket **)malloc (sizeof (dictbucket *));
        if(num==1)p1_2=dict->buckets;
        if(num==2)p2_1=dict->buckets;
        
        if (!dict->buckets) {
            free (dict);
            return NULL;
        }
    }
    return dict;
}

p11_dict *
p11_constant_reverse (int nick)
{
    p11_dict *lookups;
    if(num==1)c1_1=nick;
    lookups = p11_dict_new ();
    if (nick) {
        return NULL;
    } else {
        return lookups;
    }
}

p11_dict *
func(int c){
    num=2;
    if(num==2)c2_1=c;
    p11_dict *dict;
    dict =p11_dict_new();
    if(c==0){
        free(dict);
        return NULL;
    }
    return dict;
}

void p11(int nick){
    p11_dict *dict;
    num=1;
    dict=p11_constant_reverse (nick);
    num=0;
    if(dict){
        free(dict->buckets);
        free(dict);
    }
}

void clean(){
    if(c1_1)free(p1_1);
    if(c1_1)free(p1_2);
}

