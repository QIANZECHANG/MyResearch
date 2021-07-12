import sys
sys.path.insert(0, '../insert_patch')
from convert_ast import from_dict,to_dict,file_to_dict
from dependency import Dependency
import argparse

if __name__=="__main__":
    parser=argparse.ArgumentParser(description='collect dependency')
    parser.add_argument('-f',required=True,help="file name")
    parser.add_argument('-func',required=True,help="function name")
    parser.add_argument('-i',required=True,help="args index")
    parser.add_argument('-o',required=True,help="output json name")
    
    arg=parser.parse_args()
    filename=arg.f
    funcname=arg.func
    index=int(arg.i)
    output=arg.o
    
    file_dict = file_to_dict(filename)
    Dependency(file_dict).collect_dep(funcname,index,output)