'''
check input dependency of a function
input: Dependency(file_dict,funcname,arg_index)
output: jsonfile{funcname, variable, type,line, col}

only consider of int

todo: 
1. branch condition has dependent variables
2. array
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
        
    def collect_dep(self,funcname,index):

        self.call_func(funcname,index)
        for f in self.res.keys():
            self.res[f]["depval"]=self.dep[f]
        return json.dumps(self.res,indent=4) 
        
    def call_func(self,funcname,index):
        #variable name
        varname=self.ext[self.func[funcname]]["decl"]["type"]["args"]["params"][index]["name"]
        #initialize in res
        if self.ext[self.func[funcname]]["decl"]["type"]["args"]["params"][index]["type"]["_nodetype"]=='TypeDecl' and self.ext[self.func[funcname]]["decl"]["type"]["args"]["params"][index]["type"]["type"]["names"][0]=='int':
            vartype="int"
        else:
            vartype="others"
            
        if funcname in self.res:
            if varname in self.res[funcname]["args"].keys():
                return self.res[funcname]["retvaldep"]
            self.res[funcname]["args"][varname]=vartype
        else:
            self.res[funcname]={"args":{varname:vartype},
                                "coord":self.ext[self.func[funcname]]["coord"],
                                "retvaldep":False,
                               }
        
        #add to self.dep
        if funcname in self.dep:
            self.dep[funcname].append(varname)
        else:
            self.dep[funcname]=[varname]
            
        self.funcname=funcname
        for s in self.ext[self.func[funcname]]["body"]["block_items"]:
            if s["_nodetype"] not in self.spec:
                print({s["_nodetype"]} + " not in spec")
                continue
            else:
                self.spec[s["_nodetype"]](s)
                self.funcname=funcname
                
        return self.res[funcname]["retvaldep"]
        

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
        
        #if self.check_assignment(cur_dic):
                
        print("Assignment")
    def decl_spec(self,cur_dic):
        print("Decl")
    def return_spec(self,cur_dic):
        print("return")
        
        
    def check_assignment(self,cur_dic):
        pass