def get_type(s,decl_type):
    while True:
        if s["_nodetype"]=="PtrDecl":
            decl_type+="*"
            s=s["type"]
        elif s["_nodetype"]=="TypeDecl":
            s=s["type"]
        elif s["_nodetype"]=="IdentifierType":
            decl_type=' '.join(s["names"])+decl_type
            break
        elif s["_nodetype"]=="Struct":
            decl_type="struct "+s["name"]+decl_type
            break
    return decl_type

def get_name(s):
    s_name=s
    name=""
    while True:
        if s_name['_nodetype']=='ID':
            name=s_name['name']+name
            break
        elif s_name['_nodetype']=='StructRef':
            field=get_name(s_name["field"])
            name=s_name['type']+field+name
            s_name=s_name['name']
        elif s_name['_nodetype']=='UnaryOp':
            s_name=s_name["expr"]
            if name:
                name="(*"+get_name(s_name)+")"+name
            else:
                name="*"+get_name(s_name)
            break
        else:
            raise TypeError
    return name

def go_to_func(file_dict,line,funcname):
    s=file_dict['ext']
    if len(s)==1:
        s=s[0]
    else:
        for i in range(1,len(s)):
            coord=int(s[i]['coord'].split(":")[1])
            if coord>line:
                s=s[i-1]
                break
    if type(s)==list:
        s=s[-1]
    assert(s["decl"]["name"]==funcname)
    return s

from copy import deepcopy
def get_fuzzer_result(filename):
    file=open(filename,'r')
    fuzzer_inf=file.read()
    leak=[]
    for inf in fuzzer_inf.split("\n\n"):
        if (("Direct leak" in inf) or ("Indirect leak" in inf)):
            leak.append(inf.split("\n"))
        if  ("double-free" in inf):
            leak.append("DF")
        if  ("use-after-free" in inf):
            leak.append("UAF")
        if  ("attempting free on address" in inf) or ("SEGV" in inf):
            leak.append("NM")
    if not leak:
        return []
        # raise Exception('No Leak or have other error')
    path=[]
    for l in leak:
        if l=="DF":
            path.append("DF")
            continue
        if l=="UAF":
            path.append("UAF")
            continue
        if l=="NM":
            path.append("NM")
            continue
        data={}
        for i in range(1,len(l)):
            if("LLVMFuzzerTestOneInput" in l[i]):
                break
            cur=deepcopy(data)
            ele=l[i].split()
            
            data["coord"]=ele[4].split("/")[-1]
            data["funcname"]=ele[3]
            data["next"]=cur

        if data not in path:
            path.append(data)
    file.close()
    return path

def double_free(filename,filelist):
    file=open(filename,'r')
    fuzzer_inf=file.read()
    df=[]
    for inf in fuzzer_inf.split("\n\n"):
        if ("double-free" in inf):
            df.append(inf.split("\n"))
    if not df:
        return []
    err_index=[]
    flag=0
    for e in df[:-1]:
        for i in range(1,len(e)):
            if("free" in e[i]):
                flag=1
                continue
            if not flag and ("free" not in e[i]):
                continue
            ele=e[i].split()
            coord=ele[4].split("/")[-1]
            line=int(coord.split(":")[1])
            column=int(coord.split(":")[2])
            for s in filelist[line-1][column+8:column+11]:
                if s.isdigit():
                    err_index.append(int(s))
                    break
            break
    return err_index


def get_error_feature(err_path):
    res=[]
    for err in err_path:
        if err=="DF":
            res.append("DF")
            continue
        if err=="UAF":
            res.append("UAF")
            continue
        if err=="NM":
            res.append("NM")
            continue
        feature=[]
        while err["next"]:
            feature.append((err["coord"].split(":")[1],err["funcname"]))
            err=err["next"]
        res.append(feature)
    return res
     
def get_dynamic_value(filename):
    file=open(filename,'r')
    inf=file.read()
    inst=[]
    for i in inf.split("\n"):
        if "instrument:" in i :
            inst.append(i)
    value={}
    for v in inst:
        v=v.split()
        key=(v[4],v[3][:-1])
        if key in value:
            value[key].append(int(v[-1]))
        else:
            value[key]=[int(v[-1])]
    return value

def get_synthesis_inf(dep):
    syn_inf=[]
    for d in dep:
        tmp={"error":[],"var":{}}
        cur_tmp=tmp["var"]
        for func,v in d.items():
            if func == "error_object":
                continue
            ret=v["ret"]
            cur_tmp[func]=[]
            for var in v["dep"]:
                key=(var["name"],var["coord"].split(":")[1])
                cur_tmp[func].append({
                    "state":var["state"],
                    "type":var["type"],
                    "name":var["name"],
                    "coord":var["coord"],
                    "value":[],
                    "ret":ret
                })
        syn_inf.append(tmp)
    return syn_inf
             
def add_dynamic_value(syn_inf,filename,error_feature,err_index):
    inst = get_dynamic_value(filename)
    err = get_error_feature(get_fuzzer_result(filename))
    for v in inst.values(): 
        l=len(v)-1
        break
    if "DF" in err:
        index=err_index#double_free(filename,filelist)
        for i in index:
            syn_inf[i]["error"]+=[0]
            for func,v in syn_inf[i]["var"].items():
                for var in v:
                    key=(var["name"],var["coord"].split(":")[1])
                    if key not in inst:
                        continue
                    var["value"].append(inst[key][-1])
        return      
    if err_index:
        for i in err_index:
            syn_inf[i]["error"]+=[1]
            for func,v in syn_inf[i]["var"].items():
                for var in v:
                    key=(var["name"],var["coord"].split(":")[1])
                    if key not in inst:
                        continue
                    var["value"].append(inst[key][-1])   
        return
    tmp = error_feature.copy()
    for e in err:   
        if e not in error_feature:
            continue
        tmp.remove(e)
        i = error_feature.index(e)
        syn_inf[i]["error"]+=[0]*(l-2)+[1]
        for func,v in syn_inf[i]["var"].items():
            for var in v:
                key=(var["name"],var["coord"].split(":")[1])
                if key not in inst:
                    continue
                var["value"]+=inst[key][1:-1]
    for e in tmp:
        i = error_feature.index(e)
        syn_inf[i]["error"]+=[0]*(l-1)
        for func,v in syn_inf[i]["var"].items():
            for var in v:
                key=(var["name"],var["coord"].split(":")[1])
                if key not in inst:
                    continue
                var["value"]+=inst[key][1:-1]

def get_error_object(dep,func):
    if not dep[func]["object"][1]:
        return (dep[func]["object"][0],dep["error_object"][1],dep[func]["object"][2],dep[func]["object"][3])
    elif dep[func]["object"][1]==dep["error_object"][1]:
        return dep[func]["object"]
    else:
        o = dep["error_object"][0]
        otype = dep["error_object"][1]
        line = dep[func]["object"][2]
        if "->" in o:
            namelist=o.split("->")
            if "." in namelist[0]:
                name=dep[func]["object"][0]+"."+".".join(namelist[0].split(".")[1:])+"->"+"->".join(namelist[1:])
            else:
                name=dep[func]["object"][0]+"->"+"->".join(namelist[1:])
        elif "." in o:
            namelist=o.split(".")
            name=dep[func]["object"][0]+"."+".".join(namelist[1:])
        else:
            return 0,0,0
        return (name,otype,line,dep[func]["object"][3])
    
def clean_inf(syn_inf):
    for i in range(len(syn_inf)):
        syn_inf[i]["error"]=[]
        for v in syn_inf[i]["var"].values():
            for var in v:
                var["value"]=[]
    