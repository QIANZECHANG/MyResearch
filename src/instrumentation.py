# dep=get_dependency("fuzzing_result")

def read_file(filename):
    f=open(filename,"r")
    filelist=f.readlines()
    f.close()
    return filelist

def write_file(filename,code):
    f=open(filename,"w")
    f.write("".join(code))
    f.close()
    
def instrument(dep):
    instrument_dict={}
    for e in dep:
        for func in e.values():
            for var in func["dep"]:
                filename=var["coord"].split(":")[0]
                if filename not in instrument_dict:
                    instrument_dict[filename]=[]
                if var not in instrument_dict[filename]:
                    instrument_dict[filename].append(var)
    
    for filename in instrument_dict.keys():
        filelist=read_file(filename)
        for var in instrument_dict[filename]:
            varname=var["name"]
            state=var["state"]
            vartype=var["type"]
            line=int(var["coord"].split(":")[1])
            if "int" not in vartype:
                continue
            deref=""
            for l in vartype:
                if l=="*":
                    deref+="*"
            printf=f"printf(\"instrument: (line : {line}) {deref+varname} : %d\\n\",{deref+varname});\n"
            if state=="var":
                filelist[line-1]=filelist[line-1][:-1]+printf
            elif state=="input":
                tmp=line-1
                while filelist[tmp][-2]!="{":
                    tmp+=1
                filelist[tmp]=filelist[tmp][:-1]+printf
                
        write_file("instrumented_"+filename,filelist)
        