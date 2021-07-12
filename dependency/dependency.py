'''
check input dependency of a function
input: Dependency(file_dict,funcname,arg_index)
output: jsonfile{funcname, variable, type,line, col}

only consider of int

todo: 
1. branch condition has dependent variables
2. array
3. recursive
'''
import json
class Dependency:
    def __init__(self,dic):
        self.dic=dic
        self.funcname=None
        self.dep={}#information of depent variables
        self.res={}#result
        self.func={}#location of functions
        self.var={}#type of variables
        self.varname=None#for return_spec
        self.spec={
            "If":self.if_spec,
            "While":self.while_spec,
            "For":self.for_spec,
            "FuncCall":self.funccall_spec,
            "Assignment":self.assignment_spec,
            "Decl":self.decl_spec,
            "Return":self.return_spec
        }
        self.ext=self.dic["ext"]
        for i in range(len(self.ext)):
            if self.ext[i]["_nodetype"]=="FuncDef":
                self.func[self.ext[i]["decl"]["name"]]=i
                self.dep[self.ext[i]["decl"]["name"]]=set()
                self.var[self.ext[i]["decl"]["name"]]={}
     
    def collect_dep(self,funcname,index,out):
        self.call_func(funcname,index)
        f=open(out,"w")
        json.dump(self.res,f,indent=4) 
        
    def call_func(self,funcname,index):
        #variable name
        varname=self.ext[self.func[funcname]]["decl"]["type"]["args"]["params"][index]["name"]
        self.varname=varname
        #initialize in res
        try:
            if self.ext[self.func[funcname]]["decl"]["type"]["args"]["params"][index]["type"]["type"]["names"][0]=='int':
                vartype="int"
            else:
                vartype="others"
        except:
            vartype="others"
        #add var to self.var
        self.var[funcname][varname]=vartype
        #add var to self.res   
        if funcname in self.res:
            if varname in self.res[funcname]["args"].keys():
                return self.res[funcname]["retvaldep"][varname]
            self.res[funcname]["args"][varname]=vartype
            self.res[funcname]["retvaldep"][varname]=False
        else:
            self.res[funcname]={"args":{varname:vartype},
                                "coord":self.ext[self.func[funcname]]["coord"],
                                "retvaldep":{varname:False},
                                "dep":[]
                               }
        #add to self.dep
        self.dep[funcname].add(varname)
            
        self.funcname=funcname
        for s in self.ext[self.func[funcname]]["body"]["block_items"]:
            if s["_nodetype"] not in self.spec:
                print({s["_nodetype"]} + " not in spec")
                continue
            else:
                self.spec[s["_nodetype"]](s)
                self.funcname=funcname
                self.varname=varname
                
        return self.res[funcname]["retvaldep"][varname]
        

    def if_spec(self,cur_dic):
        print("If")
    def while_spec(self,cur_dic):
        print("While")
    def for_spec(self,cur_dic):
        print("For")
    def funccall_spec(self,cur_dic):
        print("FuncCall")
    def assignment_spec(self,cur_dic):
        #FuncCall,UnaryOp,BinaryOp,"ID","Constant"
        #left value
        var=""
        l_dict=cur_dic["lvalue"]
        while True:
            if l_dict["_nodetype"]=="ID":
                var+=l_dict["name"]
                coord=l_dict["coord"]
                break
            elif l_dict["_nodetype"]=="UnaryOp":
                var+="*"
                l_dict=l_dict["expr"]
            elif l_dict["_nodetype"]=="StructRef":
                var+=l_dict["name"]["name"]+l_dict["type"]+l_dict["field"]["name"]
                coord=l_dict["field"]["coord"]
                break
        
        if self.check_assignment(cur_dic["rvalue"]):
            #add to self.dep
            self.dep[self.funcname].add(var)
            #check type
            if "->" in var:return
            if "int" in self.var[self.funcname][var]:
                star_num = len(self.var[self.funcname][var].split())-1
                self.res[self.funcname]["dep"].append(("*"*star_num+var,coord))
        else:
            if var in self.dep[self.funcname]:
                self.dep[self.funcname].remove(var)

        print("Assignment")
    def decl_spec(self,cur_dic):
        vartype=""
        s=cur_dic["type"]
        while True:
            if s["_nodetype"]=="PtrDecl":
                vartype+=" *"
                s=s["type"]
            elif s["_nodetype"]=="TypeDecl":
                var=s["declname"]
                coord=s["coord"]
                s=s["type"]
            elif s["_nodetype"]=="IdentifierType":
                vartype=s["names"][0]+vartype
                break
            elif s["_nodetype"]=="Struct":
                vartype="struct "+s["name"]+vartype
                break
        #add var to self.var
        self.var[self.funcname][var]=vartype
        for i in range(len(vartype.split())-1,-1,-1):
            if vartype.split()[i]=="*":
                self.var[self.funcname]["*"+var]=" ".join(vartype.split()[:i])
                
        if cur_dic["init"]:
            if self.check_assignment(cur_dic["init"]):
                #add to self.dep
                self.dep[self.funcname].add(var)
                #check type
                if "int" in self.var[self.funcname][var]:
                    star_num = len(self.var[self.funcname][var].split())-1
                    self.res[self.funcname]["dep"].append(("*"*star_num+var,coord))
            else:
                if var in self.dep[self.funcname]:
                    self.dep[self.funcname].remove(var)
              
        print("Decl")
        
    def return_spec(self,cur_dic):
        if self.check_assignment(cur_dic["expr"]):
            self.res[self.funcname]["retvaldep"][self.varname]=True
        print("return")
        
        
    def check_assignment(self,cur_dic):
        #check func args
        if cur_dic["_nodetype"]=="FuncCall":
            if cur_dic["name"]["name"] == self.funcname:
                return False
            for i in range(len(cur_dic["args"]["exprs"])):
                if self.check_assignment(cur_dic["args"]["exprs"][i]):
                    tmp=self.funcname
                    res=self.call_func(cur_dic["name"]["name"],i)
                    self.funcname=tmp
                    return res
        var=""
        tmp=cur_dic
        while tmp["_nodetype"] in ["UnaryOp","StructRef","ID"]:
            if tmp["_nodetype"]=="ID":
                var+=tmp["name"]
                return var in self.dep[self.funcname] or tmp["name"] in self.dep[self.funcname]
            elif tmp["_nodetype"]=="UnaryOp":
                var+="*"
                tmp=tmp["expr"]
            elif tmp["_nodetype"]=="StructRef":
                var+=tmp["name"]["name"]+tmp["type"]+tmp["field"]["name"]
                coord=tmp["field"]["coord"]
                return var in self.dep[self.funcname]
        #check other types         
        for i in cur_dic.keys():
            if type(cur_dic[i]) is dict:
                if self.check_assignment(cur_dic[i]): 
                    return True 
            if type(cur_dic[i]) is list:
                for e in cur_dic[i]:
                    if type(e) is dict and self.check_assignment(e): 
                        return True                     
        return False