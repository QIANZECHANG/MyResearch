from convert_ast import from_dict,to_dict,file_to_dict
from localization import Localization
from pycparser import parse_file, c_parser, c_generator, c_ast
import argparse

if __name__=="__main__":
    parser=argparse.ArgumentParser(description='insert patch')
    parser.add_argument('-f',required=True,help="file name")
    parser.add_argument('-e',required=True,help="error location")
    parser.add_argument('-i',help="insert location")
    parser.add_argument('-p',required=True,help="patch")

    arg=parser.parse_args()
    
    error_line=int(arg.e.split(":")[0])
    error_col=int(arg.e.split(":")[1])
    if arg.i==None:
        flag=0
    else:
        flag=1
        insert_line=int(arg.i.split(":")[0])
        insert_col=int(arg.i.split(":")[1])
    file=arg.f
    patch=arg.p

    file_dict = file_to_dict(file)
    # get heap-object
    cur_dict,loc=Localization(file_dict,error_line,error_col).loc(1)
    obj=cur_dict[loc]["lvalue"]["name"]
    text=r"void a{if("+patch+")free("+obj+");}"
    # generate the dict of patch
    parser = c_parser.CParser() 
    patch_ast = parser.parse(text) 
    patch_dict=to_dict(patch_ast)
    patch_dict=patch_dict["ext"][0]["body"]["block_items"][0]

    if flag:# use infer output
        cur_dict,loc=Localization(file_dict,insert_line,insert_col).loc(flag)
    else:# insert to the end of a function
        cur_dict,loc=Localization(file_dict,error_line,error_col).loc(flag)


    cur_dict.insert(loc,patch_dict)

    file_ast = from_dict(file_dict)
    generator = c_generator.CGenerator()

    print(generator.visit(file_ast))

