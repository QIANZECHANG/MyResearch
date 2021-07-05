#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import json
import sys
import re
sys.path.extend(['.', '..'])
from pycparser.plyparser import Coord
from pycparser import parse_file, c_parser, c_generator, c_ast
import argparse
import sys
import json

parser=argparse.ArgumentParser(description='insert patch')
parser.add_argument('-f',required=True,help="file name")
parser.add_argument('-e',required=True,help="error location")
parser.add_argument('-i',help="insert location")
parser.add_argument('-p',required=True,help="patch")

arg=parser.parse_args()

RE_CHILD_ARRAY = re.compile(r'(.*)\[(.*)\]')
RE_INTERNAL_ATTR = re.compile('__.*__')


class CJsonError(Exception):
    pass


def memodict(fn):
    """ Fast memoization decorator for a function taking a single argument """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = fn(key)
            return ret
    return memodict().__getitem__


@memodict
def child_attrs_of(klass):
    """
    Given a Node class, get a set of child attrs.
    Memoized to avoid highly repetitive string manipulation
    """
    non_child_attrs = set(klass.attr_names)
    all_attrs = set([i for i in klass.__slots__ if not RE_INTERNAL_ATTR.match(i)])
    return all_attrs - non_child_attrs


def to_dict(node):
    """ Recursively convert an ast into dict representation. """
    klass = node.__class__

    result = {}

    # Metadata
    result['_nodetype'] = klass.__name__

    # Local node attributes
    for attr in klass.attr_names:
        result[attr] = getattr(node, attr)

    # Coord object
    if node.coord:
        result['coord'] = str(node.coord)
    else:
        result['coord'] = None

    # Child attributes
    for child_name, child in node.children():
        # Child strings are either simple (e.g. 'value') or arrays (e.g. 'block_items[1]')
        match = RE_CHILD_ARRAY.match(child_name)
        if match:
            array_name, array_index = match.groups()
            array_index = int(array_index)
            # arrays come in order, so we verify and append.
            result[array_name] = result.get(array_name, [])
            if array_index != len(result[array_name]):
                raise CJsonError('Internal ast error. Array {} out of order. '
                    'Expected index {}, got {}'.format(
                    array_name, len(result[array_name]), array_index))
            result[array_name].append(to_dict(child))
        else:
            result[child_name] = to_dict(child)

    # Any child attributes that were missing need "None" values in the json.
    for child_attr in child_attrs_of(klass):
        if child_attr not in result:
            result[child_attr] = None

    return result


def to_json(node, **kwargs):
    """ Convert ast node to json string """
    return json.dumps(to_dict(node), **kwargs)


def file_to_dict(filename):
    """ Load C file into dict representation of ast """
    ast = parse_file(filename)
    return to_dict(ast)


def file_to_json(filename, **kwargs):
    """ Load C file into json string representation of ast """
    ast = parse_file(filename, use_cpp=True)
    return to_json(ast, **kwargs)


def _parse_coord(coord_str):
    """ Parse coord string (file:line[:column]) into Coord object. """
    if coord_str is None:
        return None

    vals = coord_str.split(':')
    vals.extend([None] * 3)
    filename, line, column = vals[:3]
    return Coord(filename, line, column)


def _convert_to_obj(value):
    """
    Convert an object in the dict representation into an object.
    Note: Mutually recursive with from_dict.
    """
    value_type = type(value)
    if value_type == dict:
        return from_dict(value)
    elif value_type == list:
        return [_convert_to_obj(item) for item in value]
    else:
        # String
        return value


def from_dict(node_dict):
    """ Recursively build an ast from dict representation """
    class_name = node_dict.pop('_nodetype')

    klass = getattr(c_ast, class_name)

    # Create a new dict containing the key-value pairs which we can pass
    # to node constructors.
    objs = {}
    for key, value in node_dict.items():
        if key == 'coord':
            objs[key] = _parse_coord(value)
        else:
            objs[key] = _convert_to_obj(value)

    # Use keyword parameters, which works thanks to beautifully consistent
    # ast Node initializers.
    return klass(**objs)


def from_json(ast_json):
    """ Build an ast from json string representation """
    return from_dict(json.loads(ast_json))

class Localization:
    def __init__(self,dic,line,col):
        self.dic=dic
        self.reline=line
        self.recol=col
        self.l=None
    
    def loc(self,flag):
        if flag:
            # infer did not detect the memory error
            self.loc_return()
        else:
            # unreachable location given by infer
            self.loc_reach()
        return self.dic,self.l
    
    def loc_return(self):#localize the return
        func=-1
        for f in self.dic['ext']:
            if int(f["coord"].split(":")[1]) > self.reline:
                break
            else:
                func+=1

        if func == -1:
            print(f"loc_return: alloc_line = {self.reline}, func = -1")
            sys.exit(1)
            
        self.dic=self.dic['ext'][func]['body']['block_items']
        if self.dic[-1]["_nodetype"] == 'Return':
            self.l=-1
        else:
            self.l=len(self.dic)
        
    def loc_reach(self):#localize the unreachable location given by infer
        func=-1
        for f in self.dic['ext']:
            if int(f["coord"].split(":")[1]) > self.reline:
                break
            else:
                func+=1

        if func == -1:
            print(f"loc_reach: reach_line = {self.reline}, func = -1")
            sys.exit(1)
        
        self.dic=self.dic['ext'][func]['body']['block_items']
        i=-1
        for b in self.dic:
            loc=b["coord"].split(":")
            if int(loc[1]) > self.reline or (int(loc[1]) == self.reline and int(loc[2]) > self.recol):
                break
            else:
                i+=1
                
        self.l=i
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
        else:
            return
        
    
    def if_spec(self):
        if self.dic["iftrue"]==None:
            tf="iffalse"
        elif self.dic["iffalse"]==None:
            tf="iftrue"
        else:
            if self.reline < int(self.dic["iffalse"]["coord"].split(":")[1]):
                tf="iftrue"
            elif self.reline > int(self.dic["iffalse"]["coord"].split(":")[1]):
                tf="iffalse"
            else:
                if self.recol < int(self.dic["iffalse"]["coord"].split(":")[2]):
                    tf="iftrue"
                elif self.reline > int(self.dic["iffalse"]["coord"].split(":")[2]):
                    tf="iffalse"
                else:
                    print(f"if_spec: reach_col={self.recol}, has the same location with \"else\"")
                    sys.exit(1)
        
        self.dic=self.dic[tf]
        if self.dic["_nodetype"] == "If":
            self.if_spec()
            return
        
        self.dic=self.dic["block_items"]
        i=-1
        for b in self.dic:
            loc=b["coord"].split(":")
            if int(loc[1]) > self.reline or (int(loc[1]) == self.reline and int(loc[2]) > self.recol):
                break
            else:
                i+=1
                
        self.l=i
        self.check_type()
    
    def while_spec(self):
        pass
    def for_spec(self):
        pass


error_line=int(arg.e.split(":")[0])
error_col=int(arg.e.split(":")[1])
if arg.i==None:
    flag=1
else:
    flag=0
    insert_line=int(arg.i.split(":")[0])
    insert_col=int(arg.i.split(":")[1])
file=arg.f
patch=arg.p

file_dict = file_to_dict(file)

cur_dict,loc=Localization(file_dict,error_line,error_col).loc(0)
obj=cur_dict[loc]["lvalue"]["name"]
text=r"void a{if("+patch+")free("+obj+");}"

parser = c_parser.CParser() # パーサ
patch_ast = parser.parse(text) # パースする
patch_dict=to_dict(patch_ast)
patch_dict=patch_dict["ext"][0]["body"]["block_items"][0]

if flag:
    cur_dict,loc=Localization(file_dict,error_line,error_col).loc(flag)
else:
    cur_dict,loc=Localization(file_dict,insert_line,insert_col).loc(flag)


cur_dict.insert(loc,patch_dict)

file_ast = from_dict(file_dict)
generator = c_generator.CGenerator() # 生成器

print(generator.visit(file_ast))

