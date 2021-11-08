import os
from my_tools import *
from dependency import *
from instrumentation import *
from insert_patch import *
from program_synthesis import *
from get_heap_object import *
import argparse
import json
import time

# input the name of buggy program
def main(filename):
    t0=time.time()
    # delete comment
    os.system(f"gcc -fpreprocessed -dD -E {filename} | sed \"1d\" > _{filename}")
    # fuzzing
    os.system(f"clang-12 -g -fsanitize=address,fuzzer _{filename}")
    os.system(r"./a.out -max_total_time=5 -max_len=2 2>fuzzer_result")
    # delete include (pycparser can't analyze)
    os.system(f"cat _{filename} | sed \"/#/c\ \" > dep_{filename} ")
    
    # get dependency variable and the error
    dep,error_feature = get_dependency("fuzzer_result")
    with open('dependency.json', 'w') as f:
        json.dump(dep, f, indent=4)
    print("dependency done")
    # source instrumentation 
    inst_filename = instrument(dep)
    
    # run instrumented program
    os.system(f"clang-12 -g -fsanitize=address,fuzzer {inst_filename}")
    os.system(r"./a.out -max_total_time=5 -max_len=2 2>inst_result")
    
    # initialization of instrumentation result
    syn_inf = get_synthesis_inf(dep,"inst_result")
    # run 100 times to get more dynamic value
    for i in range(100):
        os.system(r"./a.out -max_total_time=5 -max_len=2 2>inst_result")
        add_dynamic_value(syn_inf,"inst_result")
    print("collect dynamic value done")  
    print(f"current time: {time.time()-t0}")
    with open('instrumentation.json', 'w') as f:
        json.dump(syn_inf, f, indent=4)   
    # get file list (line)
    filelist = read_file(filename)
    inst_filelist = read_file(inst_filename)
    
    print(f"have {len(error_feature)} error(s)")
    # try to fix each error
    for i in range(len(error_feature)):
        err_dep = dep[i]
        err_fea = error_feature[i]
        t1=time.time()
        t=0
        not_fixed=1 # flag
        while t<60 and not_fixed: # one error 1 min
            cur_inst_filelist=inst_filelist.copy()
            err_inf = syn_inf[i]
            # for each error, generate the patch of each function in the error patch 
            patch_cand = synthesis().synthesis(err_inf)
            # insert temporary variable in each function and keep it filelist
            patch = insert_tmp_var(filelist,patch_cand)
            # try to fix this error
            cur_filelist,not_fixed=fix(patch,err_dep,err_fea,error_feature,cur_inst_filelist)
            # if failed, instrument again and get new dynamic variable
            if not_fixed:
                print("collect new test cases")
                write_file("inst_"+filename,cur_inst_filelist)
                os.system(f"clang-12 -g -fsanitize=address,fuzzer inst_{filename}")
                for i in range(5)
                    os.system(r"./a.out -max_total_time=5 -max_len=2 2>inst_result")
                    add_dynamic_value(syn_inf,"inst_result")
            t=time.time()-t1
        # if this error is fixed
        if not not_fixed:
            # keep current patch
            filelist=cur_filelist.copy()
            # keep current instrumentation version
            inst_filelist=cur_inst_filelist.copy()
        else:
            # if time out, print error number
            print(f"failed to fix error {i}")
        os.system(r"rm leak*") 
    # write file at last
    write_file("result_"+filename,filelist)
    print(f"total time: {time.time()-t0}")
    
def fix(patch,err_dep,err_fea,error_feature,inst_filelist):
    """ 
    k: funcname
    v: filelist, patch, return location
    """
    # try the patch in each function
    for k,v in patch.items():
        if not v:
            continue
        cur_filelist=v["filelist"].copy()
        # get object type and name
        o,otype,line=get_error_object(err_dep,k)
        # if failed to get object information, try the patch in next function 
        if o == 0:
            continue
        # insert temporary variable to keap the object
        cur_filelist,o=insert_heap_object(cur_filelist,o,otype,line)
        # synthesis the patch: if(c)free(o);
        free=cur_patch(v["patch"],o)
        print(f"current patch is {free} in function {k}")
        # insert the patch before each return, to find the correct location
        for ret in v["ret"]:
            print(f"insert at {ret}")
            patch_line=int(ret["coord"].split(":")[1])
            # insert patch
            cand_filelist=insert_patch(cur_filelist,patch_line,free)
            # test patched program
            write_file("patched_"+filename,cand_filelist)
            os.system(f"clang-12 -g -fsanitize=address,fuzzer patched_{filename}")
            os.system(r"./a.out -max_total_time=5 -max_len=2 2>cur_fuzzer_result")
            # collect current error
            cur_err=get_error_feature(get_fuzzer_result("cur_fuzzer_result"))
            # same with the original error
            if error_feature == cur_err:
                print("repair a part of error")
                # repair a part of error, keep the current patch
                cur_filelist=cand_filelist.copy()
                # use for instrumentation
                inst_filelist=insert_patch(inst_filelist,patch_line,free)
                continue
            # new error happened
            flag=0
            for err in cur_err:
                if err not in error_feature:
                    print("wrong patch/location")
                    flag=1
                    # wrong patch
                    break
            if flag:
                continue
            # not in current error
            if err_fea not in cur_err:
                print("correct patch")
                # keep instrumentation version
                inst_filelist=insert_patch(inst_filelist,patch_line,free)
                return cand_filelist,0
    return None,1
                    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='file name')
    parser.add_argument('f',type=str, help='file name')
    args = parser.parse_args()
    filename=args.f

    main(filename)