#!/usr/bin/env python
# Filename: poweron_vm.py
# Function: power on some or all VMs(Only support 'VirtualOS_0XX')
###If you want to power on VirtualOS_050 to VirtualOS_055
###Use command '''python vm_poweron.py -d '10.155.32.134' -lb 50 -l 5  '''
# coding:utf-8
# Author: Well
from vm import *
import argparse
def poweron_vm_via_list(host,user,password,poweron_vm_list,is_except,is_all,is_debug):
    ###Firstly get all vmname and vmid info
    poweron_login=vm(host,user,password)
    get_vmid_command='vim-cmd vmsvc/getallvms'
    poweron_login.spawn_child.sendline(get_vmid_command)
    poweron_login.spawn_child.expect('#')
    get_vmname_file=poweron_login.spawn_child.before
    get_vmname_list=re.findall(r'\n\d+ +(\w+) +',get_vmname_file)
    debug('The all vmname list is as below',is_debug)
    debug(get_vmname_list,is_debug)
    poweron_vmname_dict=list_compare(get_vmname_list,poweron_vm_list)
    print poweron_vmname_dict
    poweron_real_list=[]
    ###Judge real poweron_vm_list
    ###### if index all has been set, ignore -l -lb -e,real poweron_vm_list is the all vmid list
    if is_all:
        print 'is_all flag has been set'
        poweron_vm=vm.power_on_all_vm(poweron_login.spawn_child)
    ###### else judge index except
    else:
        print 'is_all flag has not been set'
        if is_except:
            ### Enable except, should poweron the members in all list, occur 0 times in poweron list
            print 'is_except flag has been set'
            for key,value in poweron_vmname_dict.items():
                if value == 0:
                    poweron_real_list.append(key)
        else:
        ### Disable except ,should poweron the members in both in all list and poweron list
            print 'is_except flag has been not set'
            for key,value in poweron_vmname_dict.items():
                if value > 0:
                    poweron_real_list.append(key)
        print 'Real poweron vmname list is as below'
        print poweron_real_list
        for poweron_vmname in poweron_real_list:
            ###power on the VM firstly
            ######change name to id
            poweron_vmid=poweron_login.vmname_to_vmid(poweron_vmname,poweron_login.spawn_child)
            poweron_vm=poweron_login.power_on_vm_via_vmid(poweron_vmid,poweron_login.spawn_child)
            print 'power on Virtual HiveOS %s successfully' % poweron_vmid
    return poweron_vm

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

parse.add_argument('-a', '--all', required=False, default=False, dest='isall', action = 'store_true',
                    help='Enable all mode, all VMs will be powered on')

parse.add_argument('-tf', '--templefolder', required=False, default='VirtualOS_001',  dest='templefolder',
                    help='Temple folder name')

parse.add_argument('-list', '--list', required=False, dest='vmlist',
                    help='Configure vm list')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')

def main():
    args = parse.parse_args() 
    host=args.desip
    user=args.loginname
    password=args.loginpassword
    ### is_except=0 or 1
    is_except=args.isexcept
    is_all=args.isall
    loop_begin=args.loopbegin
    loop=args.loop
    templefolder=args.templefolder
    templename=re.sub(r'\d+$','',templefolder)
    vm_list_str=args.vmlist
    is_debug=args.is_debug
    if vm_list_str:
        vm_list=str_to_list(vm_list_str)
    else:
        vm_list=[]
        for i in range(loop):
            vm=i+loop_begin
            vm_list.append(vm)    
    poweron_vm_list=[]
    for vm_num in vm_list:
        if templefolder == 'VirtualOS_001':
            poweron_vm_list.append('VirtualOS_%03d' % vm_num)
        else:
            poweron_vm_list.append('%s%d' % (templename,vm_num))
    print 'power on vmname range is as below'
    print poweron_vm_list
    poweron_vm_result=poweron_vm_via_list(host,user,password,poweron_vm_list,is_except,is_all,is_debug)
    return poweron_vm_result

if __name__=='__main__':
    try:
        poweron_vm_result=main()
    except Exception,e:
        print str(e)
    else:
        if poweron_vm_result:
            poweron_vm_result.close(force=True)
            print 'Power on all VMs successfully'
        else:
            print 'Power on all VMs failed'