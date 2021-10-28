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