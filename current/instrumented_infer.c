typedef struct _p11_dict {
    struct p11_dictbucket **buckets;
}p11_dict;

typedef struct p11_dictbucket {
    struct p11_dictbucket *next;
} dictbucket;

p11_dict *
p11_dict_new (){
    p11_dict *dict;**(*p)->a.b=b+c;
    dict = malloc (sizeof (p11_dict));
    if (dict) {
        dict->buckets = (dictbucket **)malloc (sizeof (dictbucket *));
        if (!dict->buckets) {
            free (dict);
            return NULL;
        }
    }
    return dict;
}


p11_dict *
func(int c){
    p11_dict *dict;
    dict =p11_dict_new();
    if(c==0){
        return NULL;
    }
    return dict;
}

p11_dict *
p11_constant_reverse (int nick)
{printf("instrument: (line : 35) nick : %d\n",nick);
    p11_dict *lookups;
    lookups = p11_dict_new ();
    if (nick) {
        return NULL;
    } else {
        return lookups;
    }
}

void p11(int nick){
    p11_dict *dict;
    dict=p11_constant_reverse (nick);
    if(dict){
        free(dict->buckets);
        free(dict);
    }
}
