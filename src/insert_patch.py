def insert_tmp_var(filelist,patch_cand):
    patch={}
    for func,patch_dict in patch_cand.items():
        cur_filelist=filelist.copy()
        retloc=patch_dict["opr"][0]["ret"]
        patch[func]={"patch":None,"ret":retloc}
        if patch_dict["op"]=="1":
            continue
        patchlist=[]
        for opr in patch_dict["opr"]:
            if opr["name"]=="_const":
                patchlist.append(str(opr["const"]))
            else:
                line=int(opr["coord"].split(":")[1])
                state=opr["state"]
                insert_stat=f"int tmp_{opr['name']} = {opr['name']};\n"
                patchlist.append("tmp_"+opr["name"])
                if state=="var":
                    cur_filelist[line-1]=cur_filelist[line-1][:-1]+insert_stat
                elif state=="input":
                    tmp=line-1
                    while len(cur_filelist[tmp])<2 or cur_filelist[tmp][-2]!="{":
                        tmp+=1
                    cur_filelist[tmp]=cur_filelist[tmp][:-1]+insert_stat
                for ret in opr["ret"]:
                    if ret in retloc and line>int(ret["coord"].split(":")[1]):
                        retloc.remove(ret)
        patch[func]["patch"]=patchlist[0]+patch_dict["op"]+patchlist[1]
        patch[func]["filelist"]=cur_filelist
    return patch
            
def insert_heap_object(filelist,o,otype,line):
    insert_stat=f"{otype} tmp_{o} = {o};\n"
    filelist[line-1]=filelist[line-1][:-1]+insert_stat
    return filelist,"tmp_"+o

def cur_patch(patch,o):
    if patch:
        return f"if({patch})free({o});"
    else: 
        return f"free({o});"
    

def insert_patch(filelist,line,patch):
    num=0
    for c in filelist[line-1]:
        if c == " ":
            num+=1
        else:
            break
    filelist[line-1]=filelist[line-1][:num]+patch+filelist[line-1][num:]
    return filelist