from z3 import *
from itertools import combinations as comb

class synthesis:
    def __init__(self):
        pass    
    def tautology(self,a):
        return True
    '''
    def var(self,a):  
        return a!=0
    def not_var(self,a):
        return a==0
    '''
    def equ(self,a,c):
        return a==c
    def neq(self,a,c):
        return a!=c
    def leq(self,a,c):
        return a<=c
    def lss(self,a,c):
        return a<c
    def geq(self,a,c):
        return a>=c
    def gtr(self,a,c):    
        return a>c

        
    def unary_op(self,error,var):
        op={
            "1":self.tautology
        }
        res={}
        for name,spec in op.items():
            for ele in var:
                if len(ele["value"])!=len(error):
                    continue
                s=Solver()
                for i in range(len(error)):
                    if error[i]:
                        s.add(spec(ele["value"][i]))
                    else:
                        s.add(Not(spec(ele["value"][i])))
                sat=s.check()
                if sat==z3.z3.sat:
                    res["op"]=name
                    res["opr"]=[]
                    res["opr"].append({
                        "state":ele["state"],
                        "type":ele["type"],
                        "name":ele["name"],
                        "coord":ele["coord"],
                        "ret":ele["ret"]
                    })
                    return sat,res
        return z3.z3.unsat,res
                
    def binary_op(self,error,var):
        op={
            "==":self.equ,
            "!=":self.neq,
            "<=":self.leq,
            "<" :self.lss,
            ">=":self.geq,
            ">" :self.gtr,
        }
        res={}
        #var op constant
        for name,spec in op.items():
            for ele in var:
                if len(ele["value"])!=len(error):
                    continue
                s=Solver()
                cons=Int('constant')
                for i in range(len(error)):
                    if error[i]:
                        s.add(spec(ele["value"][i],cons))
                    else:
                        s.add(Not(spec(ele["value"][i],cons)))
                sat=s.check()
                if sat==z3.z3.sat:
                    res["op"]=name
                    res["opr"]=[]
                    res["opr"].append({
                        "state":ele["state"],
                        "type":ele["type"],
                        "name":ele["name"],
                        "coord":ele["coord"],
                        "ret":ele["ret"]
                    })
                    res["opr"].append({
                        "state":"element",
                        "type":"int",
                        "name":"_const",
                        "coord":None,
                        "const":s.model()[cons],
                        "ret":ele["ret"]
                    })
                    return sat,res
        #var op var
        for name,spec in op.items():
            var_comb=comb(var,2)
            for ele1,ele2 in var_comb:
                if len(ele1["value"])!=len(error) or len(ele2["value"])!=len(error):
                    continue
                s=Solver()
                for i in range(len(error)):
                    if error[i]:
                        s.add(spec(ele1["value"][i],ele2["value"][i]))
                    else:
                        s.add(Not(spec(ele1["value"][i],ele2["value"][i])))
                sat=s.check()
                if sat==z3.z3.sat:
                    res["op"]=name
                    res["opr"]=[]
                    res["opr"].append({
                        "state":ele1["state"],
                        "type":ele1["type"],
                        "name":ele1["name"],
                        "coord":ele1["coord"],
                        "ret":ele1["ret"]
                    })
                    res["opr"].append({
                        "state":ele2["state"],
                        "type":ele2["type"],
                        "name":ele2["name"],
                        "coord":ele2["coord"],
                        "ret":ele2["ret"]
                    })
                    return sat,res
            
            
        return z3.z3.unsat,res

    def triple_op(self,a,b,c):
        pass
    
    def synthesis(self,data):
        error=data["error"]
        out={}
        for func,var in data["var"].items():
            out[func]=None
            #unary operator
            sat,res=self.unary_op(error,var)
            if sat==z3.z3.sat:
                out[func]=res
                continue
            #binary operator
            sat,res=self.binary_op(error,var)
            if sat==z3.z3.sat:
                out[func]=res
                continue
        return out