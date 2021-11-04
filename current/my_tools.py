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
    if not leak:
        raise Exception('No Leak or have other error')
    path=[]
    for l in leak:
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

def get_synthesis_inf(dep,filename):
    inst = get_dynamic_value(filename)
    syn_inf=[]
    for v in inst.values(): 
        l=len(v)-1
        break
    for d in dep:
        tmp={"error":[0]*(l-1)+[1],"var":{}}
        cur_tmp=tmp["var"]
        for func,v in d.items():
            ret=v["ret"]
            cur_tmp[func]=[]
            for var in v["dep"]:
                key=(var["name"],var["coord"].split(":")[1])
                if key not in inst:
                    continue
                cur_tmp[func].append({
                    "state":var["state"],
                    "type":var["type"],
                    "name":var["name"],
                    "coord":var["coord"],
                    "value":inst[key][:-1],
                    "ret":ret
                })
        syn_inf.append(tmp)
    return syn_inf
             
def add_dynamic_value(syn_inf,filename):
    inst = get_dynamic_value(filename)
    for v in inst.values(): 
        l=len(v)-1
        break
    for d in syn_inf:
        d["error"]+=[0]*(l-1)+[1]
        for func,v in d["var"].items():
            for var in v:
                key=(var["name"],var["coord"].split(":")[1])
                if key not in inst:
                    continue
                var["value"]+=inst[key][:-1]
               