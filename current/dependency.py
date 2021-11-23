from convert_ast import from_dict,to_dict,file_to_dict
from pycparser import parse_file, c_parser, c_generator, c_ast
from my_tools import go_to_func,get_type,get_fuzzer_result,get_name
from get_heap_object import *
from my_tools import *

def get_dependency(fuzzer):
    err_path=get_fuzzer_result(fuzzer)
    dependency=[]
    for err in err_path:
        if err=="DF" or err=="UAF":
            raise Exception(f'{err} happened')
        var={}
        while err["next"]:
            filename="dep"+err["coord"].split(":")[0] 
            file_dict = file_to_dict(filename)
            line=int(err["coord"].split(":")[-2])
            o,otype=get_heap_object(file_dict,line)#heap object
            funcname=err["funcname"]
            func_dict=go_to_func(file_dict,line,funcname)
            dep, ret=Dependency(func_dict).result()
            var[funcname]={"dep":dep,"ret":ret,"object":(o,otype,line,int(func_dict["coord"].split(":")[1]))}
            err=err["next"]
        var["error_object"]=(o,otype,line)
        dependency.append(var)
    return dependency,get_error_feature(err_path)

def get_func_tail(cur_dict):
    coord=cur_dict["coord"]
    for v in cur_dict.values():
        if not v:
            continue
        if type(v)==dict:
            coord=get_func_tail(v)
        elif type(v)==list:
            if type(v[-1])==dict:
                coord=get_func_tail(v[-1])
    return coord

class Dependency:
    def __init__(self,dic):
        self.dic=dic
        self.dep=[]#information of depent variables
        self.cur_dep=set()
        self.var={}
        self.ret=[]
        self.spec={
            "If":self.if_spec,
            "While":self.while_spec,
            "For":self.for_spec,
            "FuncCall":self.funccall_spec,
            "Assignment":self.assignment_spec,
            "Decl":self.decl_spec,
            "Return":self.return_spec
        }
        try:
            for arg in dic["decl"]["type"]["args"]["params"]:
                param={
                    "name":arg["name"],
                    "state":"input",
                    "type":get_type(arg["type"],""),
                    "coord":arg["coord"]
                }
                self.cur_dep.add(arg["name"])
                self.dep.append(param)
        except:
            pass
    def result(self):
        for stat in self.dic["body"]["block_items"]:
            if stat["_nodetype"] not in self.spec:
                #print("_nodetype is "+stat["_nodetype"])
                continue
            self.spec[stat["_nodetype"]](stat)
        tail=get_func_tail(stat)
        tail_line=tail.split(":")[1]
        for ret in self.ret:
            if ret["coord"].split(":")[1] == tail_line:
                return self.dep, self.ret
        return self.dep, self.ret+[{"coord":tail}]        

    def if_spec(self,cur_dic):
        if_true=cur_dic["iftrue"]
        if_false=cur_dic["iffalse"]
        if if_true and if_true["_nodetype"]=="Compound":
            for stat in if_true["block_items"]:
                if stat["_nodetype"] not in self.spec:
                    #print("_nodetype is "+stat["_nodetype"])
                    continue
                self.spec[stat["_nodetype"]](stat)
            
        if if_false and if_false["_nodetype"]=="Compound":
            for stat in if_false["block_items"]:
                if stat["_nodetype"] not in self.spec:
                    #print("_nodetype is "+stat["_nodetype"])
                    continue
                self.spec[stat["_nodetype"]](stat)
            
        #print("If")
    def while_spec(self,cur_dic):
        pass
        """
        if cur_dic["stmt"] and cur_dic["stmt"]["_nodetype"]=="Compound":
            for stat in cur_dic["stmt"]["block_items"]:
                if stat["_nodetype"] not in self.spec:
                    continue
                self.spec[stat["_nodetype"]](stat)
        """
    def for_spec(self,cur_dic):
        pass
        """
        if cur_dic["stmt"] and cur_dic["stmt"]["_nodetype"]=="Compound":
            for stat in cur_dic["stmt"]["block_items"]:
                if stat["_nodetype"] not in self.spec:
                    continue
                self.spec[stat["_nodetype"]](stat)
        """
    def funccall_spec(self,cur_dic):
        pass
        #print("FuncCall")
    def assignment_spec(self,cur_dic):
        #FuncCall,UnaryOp,BinaryOp,"ID","Constant"
        #left value
        l_dict=cur_dic["lvalue"]
        varname=get_name(l_dict)

        if self.check_dependency(cur_dic["rvalue"]):
            #add to self.dep
            self.cur_dep.add(varname)
            if varname in self.var:
                param={
                    "name":varname,
                    "state":"var",
                    "type":self.var[varname],
                    "coord":cur_dic["lvalue"]["coord"]
                }
                self.dep.append(param)
        else:
            if varname in self.cur_dep:
                self.cur_dep.remove(varname)

        #print("Assignment")
    def decl_spec(self,cur_dic):        
        if cur_dic["init"]:
            if self.check_dependency(cur_dic["init"]):
                vartype=get_type(cur_dic["type"],"")
                varname=cur_dic["name"]
                #add var to self.var
                self.var[varname]=vartype
                #add to self.dep
                self.cur_dep.add(varname)
                param={
                    "name":varname,
                    "state":"var",
                    "type":vartype,
                    "coord":cur_dic["init"]["coord"]
                }
                self.dep.append(param)
        
    def return_spec(self,cur_dic):
        self.ret.append({"coord":cur_dic["coord"]})
        #print("return")
           
    def check_dependency(self,cur_dic):
        #check func args
        if cur_dic["_nodetype"]=="FuncCall":
            try:
                for i in range(len(cur_dic["args"]["exprs"])):
                    #print("name "+cur_dic["name"]["name"])
                    if self.check_dependency(cur_dic["args"]["exprs"][i]):
                        return True
            except:
                pass
            return False
        try:
            name=get_name(cur_dic["name"])
            if name in self.cur_dep:
                return True
        except:
            pass
        try:
            name=get_name(cur_dic)
            if name in self.cur_dep:
                return True
        except:
            pass
        try:
            if "name" in cur_dic and cur_dic["name"]:
                if cur_dic["name"] in self.cur_dep:
                    return True
            if "names" in cur_dic and cur_dic["names"]:
                for n in cur_dic["names"]:
                    if n in self.cur_dep:
                        return True
        except:
            pass
        #check other types         
        for i in cur_dic.keys():
            if type(cur_dic[i]) is dict:
                if self.check_dependency(cur_dic[i]): 
                    return True 
            if type(cur_dic[i]) is list:
                for e in cur_dic[i]:
                    if type(e) is dict and self.check_dependency(e): 
                        return True                     
        return False