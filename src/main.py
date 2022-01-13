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
    fuzztime=0
    # delete comment
    os.system(f"gcc -fpreprocessed -dD -E {filename} | sed \"1d\" > _{filename}")
    # fuzzing
    print("fuzzing")
    os.system(f"clang-12 -g -fsanitize=address,fuzzer _{filename}")
    err_num=0
    for _ in range(10):
        t_fuzz=time.time()
        os.system(r"./a.out -max_total_time=5 -max_len=2 2>fuzzer_result")
        fuzztime+=time.time()-t_fuzz
        err_path=get_fuzzer_result("fuzzer_result")
        if len(err_path)>err_num:
            err_num=len(err_path)
            os.system("cat fuzzer_result > tmp")
    if err_num==0:
        print("no error")
        return
    os.system("cat tmp > fuzzer_result")
    os.system("rm -f tmp")
    print("fuzzing done")
    # delete include (pycparser can't analyze)
    os.system(f"cat _{filename} | sed \"/#/c\ \" > dep_{filename} ")

    t_depstart=time.time()
    # get dependency variable and the error
    dep,error_feature = get_dependency("fuzzer_result")
    print(f"static analysis: {time.time()-t_depstart}\n")

    _error_feature=error_feature.copy()
    with open('dependency.json', 'w') as f:
        json.dump(dep, f, indent=4)
    print("dependency done")
    # get file list (line)
    filelist = read_file("_"+filename)
    # source instrumentation 
    inst_filename = instrument(dep)

    # initialization of instrumentation result
    syn_inf = get_synthesis_inf(dep)
    os.system(f"clang-12 -g -fsanitize=address,fuzzer {inst_filename}")
    # run 10 times to get more dynamic value
    for i in range(10):
        t_fuzz=time.time()
        os.system(r"./a.out -max_total_time=5 -max_len=2 2>inst_result")
        fuzztime+=time.time()-t_fuzz
        add_dynamic_value(syn_inf,"inst_result",_error_feature,[])
        
    print("collect dynamic value done")
    print(f"fuzzing time: {fuzztime}")  
    print(f"current time: {time.time()-t0}")    
    print(f"have {len(error_feature)} error(s)")
    
    queue=[i for i in range(len(error_feature))]
    to_fix_list=[]
    # try to fix each error
    # for i in range(len(error_feature)):
    flag=0
    while queue and flag!=len(queue):
        i=queue.pop(0)
        err_dep = dep[i]
        err_fea = _error_feature[i]
        t1=time.time()
        t=0
        not_fixed=1 # flag
        p=None
        while t<120 and not_fixed: # one error 1 min
            err_inf = syn_inf[i]
            # for each error, generate the patch of each function in the error patch 
            patch_cand = synthesis().synthesis(err_inf)
            # insert temporary variable in each function and keep it filelist
            patch = insert_tmp_var(filelist,patch_cand)
            if p==patch:
                break
            p=patch
            # try to fix this error
            cur_filelist,not_fixed,ft=fix(patch,err_dep,err_fea,error_feature,i,dep)
            fuzztime+=ft
            # if failed, instrument again and get new dynamic variable
            if not_fixed==1:
                print("collect error test cases")
                add_dynamic_value(syn_inf,"cur_fuzzer_result",_error_feature,[i])
                os.system(f"clang-12 -g -fsanitize=address,fuzzer {inst_filename}")
                for _ in range(10):
                    t_fuzz=time.time()
                    os.system(r"./a.out -max_total_time=5 -max_len=2 2>inst_result")
                    fuzztime+=time.time()-t_fuzz
                    add_dynamic_value(syn_inf,"inst_result",_error_feature,[])
            t=time.time()-t1
        if(t>=120):
            print("time out")
        # if this error is fixed
        if not_fixed==0:
            print(f"fixed error {i}, error feature: {err_fea}")
            # keep current patch
            filelist=cur_filelist.copy()
            write_file("cur_"+filename,cur_filelist)
            error_feature.remove(_error_feature[i])
            flag=0
            if queue:
                # clean dynamic value and collect new values
                clean_inf(syn_inf)
                new_instrument(cur_filelist.copy(),dep,inst_filename)
                print("collect new test cases")
                os.system(f"clang-12 -g -fsanitize=address,fuzzer {inst_filename}")
                for _ in range(10):
                    t_fuzz=time.time()
                    os.system(r"./a.out -max_total_time=5 -max_len=2 2>inst_result")
                    fuzztime+=time.time()-t_fuzz
                    add_dynamic_value(syn_inf,"inst_result",_error_feature,[])
        else:
            # if time out, print error number
            print(f"failed to fix error {i}")
            queue.append(i)
            flag+=1

                
        os.system(r"rm -f leak*")
        os.system(r"rm -f crash*")
    # write file at last
    os.system(f"rm -f *_{filename}")
    os.system(f"rm -f *_result")
    os.system(f"rm a.out")
    os.system(f"rm -f check_and_instrument.c")
    write_file("result_"+filename,filelist)
    with open('syn_inf.json', 'w') as f:
        json.dump(syn_inf, f, indent=4)
    print(f"fuzzing time: {fuzztime}") 
    print(f"total time: {time.time()-t0}")
    
def fix(patch,err_dep,err_fea,error_feature,i,dep):
    """ 
    k: funcname
    v: filelist, patch, return location
    """
    fuzztime=0
    # try the patch in each function
    for k,v in patch.items():
        if not v:
            continue
        cur_filelist=v["filelist"].copy()
        # get object type and name
        o,otype,line,head=get_error_object(err_dep,k)
        # if failed to get object information, try the patch in next function 
        if o == 0:
            continue
        # insert temporary variable to keap the object
        cur_filelist,o=insert_heap_object(cur_filelist.copy(),o,otype,line,head,i)
        # synthesis the patch: if(c)free(o);
        free=cur_patch(v["patch"],o)
        print(f"current patch is {free} in function {k}")
        # insert the patch before each return, to find the correct location
        for ret in v["ret"]:
            print(f"insert at {ret}")
            patch_line=int(ret["coord"].split(":")[1])
            # insert patch
            cand_filelist=insert_patch(cur_filelist.copy(),patch_line,free)
            # test patched program
            new_instrument(cand_filelist.copy(),dep,"check_and_instrument.c")
            #write_file("patched_"+filename,cand_filelist)
            os.system(f"clang-12 -g -fsanitize=address,fuzzer check_and_instrument.c")
            max_err=[]
            f=0
            for _ in range(10):
                t=time.time()
                os.system(r"./a.out -max_total_time=5 -max_len=2 2>cur_fuzzer_result")
                fuzztime+=time.time()-t
                if time.time()-t>=5:
                    break
                #err_path=get_fuzzer_result("cur_fuzzer_result")
                cur_err=get_error_feature(get_fuzzer_result("cur_fuzzer_result"))
                if "NM" in cur_err:
                    print("wrong patch/location")
                    return None,1,fuzztime
                if len(cur_err)>len(max_err):
                    max_err=cur_err.copy()  
                    f=1
                    os.system("cat cur_fuzzer_result > tmp")
            if f:
                os.system("cat tmp > cur_fuzzer_result")
                os.system("rm -f tmp")
            # collect current error
            cur_err=get_error_feature(get_fuzzer_result("cur_fuzzer_result"))
            # same with the original error
            if error_feature == cur_err:
                print("repair a part of error")
                # repair a part of error, keep the current patch
                cur_filelist=cand_filelist.copy()
                continue
            # new error happened
            flag=0
            for err in cur_err:
                if err=="DF" or err=="UAF":
                    print("wrong patch/location")
                    flag=1
                    # wrong patch
                    break
                if err not in error_feature:
                    for e in error_feature:
                        if e[-1]==err[-1]:
                            print("wrong patch/location")
                            flag=1
                            # wrong patch
                            break
            if flag:
                continue
            # not in current error
            if err_fea not in cur_err:
                print("correct patch")
                return cand_filelist,0,fuzztime
    return None,1,fuzztime

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='file name')
    parser.add_argument('f',type=str, help='file name')
    args = parser.parse_args()
    filename=args.f

    main(filename)
