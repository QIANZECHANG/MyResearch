'''
localization of dict generated from convert_ast
input: Localization(file_dict,line,col).loc(flag)
output: cur_dict_loc, insert_index
'''
class Localization:
    def __init__(self,dic,line,col):
        self.dic=dic
        self.line=line
        self.col=col
        self.l=None
    
    def loc(self,flag):
        if flag:
            # if input the precise location
            self.loc_reach()     
        else:
            # if only want to know the location of the end of a function
            self.loc_return()
        return self.dic,self.l
    
    def loc_return(self):#localize the return or end location
        func=-1
        for f in self.dic['ext']:
            if int(f["coord"].split(":")[1]) > self.line:
                break
            else:
                func+=1

        if func == -1:
            print(f"loc_return: alloc_line = {self.line}, func = -1")
            sys.exit(1)
            
        self.dic=self.dic['ext'][func]['body']['block_items']
        if self.dic[-1]["_nodetype"] == 'Return':
            self.l=-1
        else:
            self.l=len(self.dic)
        
    def loc_reach(self):#localize the precise location
        func=-1
        for f in self.dic['ext']:
            if int(f["coord"].split(":")[1]) > self.line:
                break
            else:
                func+=1

        if func == -1:
            print(f"loc_reach: reach_line = {self.line}, func = -1")
            sys.exit(1)
        
        self.dic=self.dic['ext'][func]['body']['block_items']
        i=0
        for b in self.dic:
            loc=b["coord"].split(":")
            if int(loc[1]) > self.line or (int(loc[1]) == self.line and int(loc[2]) > self.col):
                break
            else:
                i+=1
        self.l=i        
        if i:self.l=i-1
        self.check_type()
        
    def check_type(self):#block and block index
        if self.dic[self.l]["_nodetype"] == "If":
            self.dic=self.dic[self.l]
            self.if_spec()# {"type":"If","node":{"type": , ...}}
        elif self.dic[self.l]["_nodetype"] == "While":
            self.dic=self.dic[self.l]
            self.while_spec()
        elif self.dic[self.l]["_nodetype"] == "For":
            self.dic=self.dic[self.l]
            self.for_spec()
        elif self.dic[self.l]["_nodetype"] == "Assignment":
            if int(self.dic[self.l]["rvalue"]["coord"].split(":")[2]) < self.col:
                self.l+=1
            return
        else:
            return
        
    
    def if_spec(self):
        if self.dic["iftrue"]==None:
            tf="iffalse"
        elif self.dic["iffalse"]==None:
            tf="iftrue"
        else:
            if self.line < int(self.dic["iffalse"]["coord"].split(":")[1]):
                tf="iftrue"
            elif self.line > int(self.dic["iffalse"]["coord"].split(":")[1]):
                tf="iffalse"
            else:
                if self.col < int(self.dic["iffalse"]["coord"].split(":")[2]):
                    tf="iftrue"
                elif self.line > int(self.dic["iffalse"]["coord"].split(":")[2]):
                    tf="iffalse"
                else:
                    print(f"if_spec: reach_col={self.col}, has the same location with \"else\"")
                    sys.exit(1)
        
        
        if self.dic[tf]["_nodetype"] == "If":
            self.dic=self.dic[tf]
            self.if_spec()
            return
        if self.dic[tf]["_nodetype"] != "Compound":
            self.dic[tf]={'_nodetype': 'Compound',
                      'coord': '',
                      'block_items': [self.dic[tf]]}
            
        self.dic=self.dic[tf]["block_items"]
        i=0
        for b in self.dic:
            loc=b["coord"].split(":")
            if int(loc[1]) > self.line or (int(loc[1]) == self.line and int(loc[2]) > self.col):
                break
            else:
                i+=1
        self.l=i
        if i:self.l=i-1
        self.check_type()
    
    def while_spec(self):
        pass
    def for_spec(self):
        pass