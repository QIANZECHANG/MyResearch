from convert_ast import from_dict,to_dict,file_to_dict
from pycparser import parse_file, c_parser, c_generator, c_ast
from my_tools import go_to_func,get_type,get_fuzzer_result,get_name

#line number to dict 
def localization(ast_dict,line):
    s=ast_dict
    if type(s)==dict:
        coord=int(s['coord'].split(":")[1])
        if coord==line:
            return s
        for v in s.values():
            if not v:
                continue
            elif type(v)==dict:
                if int(v['coord'].split(":")[1])>line:
                    return localization(tmp,line)
            elif type(v)==list:
                if int(v[0]['coord'].split(":")[1])>line:
                    return localization(tmp,line)
            else:
                continue
            tmp=v
        return localization(tmp,line)

    elif type(s)==list:
        if len(s)==1:
            return localization(s[0],line)
        for i in range(1,len(s)):
            coord=int(s[i]['coord'].split(":")[1])
            if coord>line:
                return localization(s[i-1],line)
        return localization(s[-1],line)
    
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

def decl_type_in_func(file_dict,line,name):
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
    
    s=s['body']['block_items']
    for item in s:
        if item['_nodetype']=='Decl':
            if item['name']==name:
                return get_type(item['type'],'')
            
def get_heap_object(file_dict,line):
    s=localization(file_dict['ext'],line)
    decl_type=''
    if(s['_nodetype']=='Decl'):
        name=s['name']
        s=s['type']
        decl_type=get_type(s,decl_type)
        
    elif(s['_nodetype']=='Assignment'):
        s_name=s['lvalue']
        name=get_name(s_name)
                
        s_type=s['rvalue']
        if s_type['_nodetype']=='FuncCall':
            try:
                s_type=s_type['args']['exprs'][0]['expr']['type']
                decl_type=get_type(s_type,decl_type)
                decl_type+="*"
            except:
                decl_type=decl_type_in_func(file_dict,line,name)
            
        elif s_type['_nodetype']=='Cast':
            s_type=s_type['to_type']['type']
            decl_type=get_type(s_type,decl_type)
            
    else:
        print("(heap_object_type/get_heap_object) Can not get heap object, nodetype is : "+s['_nodetype'])

    return name,decl_type