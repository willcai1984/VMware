#!/usr/bin/env python
# Filename: delete_vm.py
# Function: delete some or all VMs(Only support 'VirtualOS_0XX')
###If you want to delete VirtualOS_050 to VirtualOS_055
###Use command '''python vm_delete.py -d '10.155.32.134' -lb 50 -l 5  '''
# coding:utf-8
# Author: Well
from vm import *
import pexpect,re,argparse

def range_poweroff_unreg_del_vm(host,user,password,del_vmname_list,is_except):
    ###Firstly get all vmname and vmid info
    del_login=vm(host,user,password)
    get_vmid_command='vim-cmd vmsvc/getallvms'
    del_login.spawn_child.sendline(get_vmid_command)
    del_login.spawn_child.expect('#')
    get_vmname_file=del_login.spawn_child.before
    get_vmname_list=re.findall(r'\n\d+ +(\w+) +',get_vmname_file)
    print 'The all vmname list is as below'
    print get_vmname_list
    del_vmname_dict=list_compare(get_vmname_list,del_vmname_list)
    del_vmname_list=[]
    if is_except:
        ### Enable except, should delete the members in all list, occur 0 times in del list
        for key,value in del_vmname_dict.items():
            if value == 0:
                del_vmname_list.append(key)
    else:
        ### Disable except ,should delete the members in both in all list and del list
        for key,value in del_vmname_dict.items():
            if value > 0:
                del_vmname_list.append(key)
    print 'Real delete vmname list is as below'
    print del_vmname_list
    for del_vmname in del_vmname_list:
        ###power off the VM firstly
        ######change name to id
        del_vmid=del_login.vmname_to_vmid(del_vmname,del_login.spawn_child)
        del_poweroff_vm=del_login.power_off_vm_via_vmid(del_vmid,del_login.spawn_child)
        print 'Power off Virtual HiveOS %s successfully' % del_vmid
        ###unregister VM
        ######
        vmx_path='/vmfs/volumes/datastore1/%s/VirtualOS_001.vmx' % del_vmname
        del_unreg_vm=del_login.unreg_vm(vmx_path,del_poweroff_vm)
        ###rm the folder
        vm_folder_path='/vmfs/volumes/datastore1/%s' % del_vmname
        del_vm_result=del_login.rm_vm_folder(vm_folder_path,del_unreg_vm)
        print 'Delete VM %s successfully' %  del_vmname
    return del_vm_result

parse = argparse.ArgumentParser(description='Delete VMs on Blade server')
###Cannot use -h, conflict with the help argument
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='root', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-l', '--loopnum', required=False, default=1, type=int,  dest='loop',
                    help='Loop times')                    

parse.add_argument('-lb', '--loopbegin', required=False, default=1, type=int, dest='loopbegin',
                    help='loop begin number')

parse.add_argument('-e', '--except', required=False, default=False, dest='isexcept', action = 'store_true',
                    help='Enable except mode, all VMs except your set range will be deleted')

def main():
    args = parse.parse_args() 
    host=args.desip
    user=args.loginname
    password=args.loginpassword
    ### is_except=0 or 1
    is_except=args.isexcept
    del_begin=args.loopbegin
    del_loop=args.loop
    del_vmname_list=[]
    for del_num in range(del_loop):
        del_vmname_list.append('VirtualOS_%03d' % (del_begin+del_num))
    del_vm_result=range_poweroff_unreg_del_vm(host,user,password,del_vmname_list,is_except)
    return del_vm_result
if __name__=='__main__':
    try:
        del_vm_result=main()
    except Exception,e:
        print str(e)
    else:
        del_vm_result.close(force=True)
        print 'Delete VM process is over'