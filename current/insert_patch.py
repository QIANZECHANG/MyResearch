def insert_tmp_var(filelist,patch_dict):
    if patch_dict["opr"]=="1":
        return filelist,None
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
                filelist[line-1]=filelist[line-1][:-1]+insert_stat
            elif state=="input":
                tmp=line-1
                while filelist[tmp][-2]!="{":
                    tmp+=1
                filelist[tmp]=filelist[tmp][:-1]+insert_stat
    
    return filelist,patchlist[0]+patch_dict["op"]+patchlist[1]
            
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
    filelist[line-1]=patch+filelist[line-1]
    return filelist