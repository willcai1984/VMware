#!/usr/bin/env python
# Filename: poweroff_vm.py
# Function: power off some or all VMs(Only support 'VirtualOS_0XX')
###If you want to power off VirtualOS_050 to VirtualOS_055
###Use command '''python poweroff_vm.py -d '10.155.32.134' -lb 50 -l 5  '''
# coding:utf-8
# Author: Well
from vm import *
import argparse
def poweroff_vm_via_list(host,user,password,poweroff_vm_list,is_except,is_all,is_debug):
    ###Firstly get all vmname and vmid info
    poweroff_login=vm(host,user,password)
    get_vmid_command='vim-cmd vmsvc/getallvms'
    poweroff_login.spawn_child.sendline(get_vmid_command)
    poweroff_login.spawn_child.expect('#')
    get_vmname_file=poweroff_login.spawn_child.before
    get_vmname_list=re.findall(r'\n\d+ +(\w+) +',get_vmname_file)
    debug('The all vmname list is as below',is_debug)
    debug(get_vmname_list,is_debug)
    poweroff_vmname_dict=list_compare(get_vmname_list,poweroff_vm_list)
    print poweroff_vmname_dict
    poweroff_real_list=[]
    ###Judge real poweroff_vm_list
    ###### if index all has been set, ignore -l -lb -e,real poweroff_vm_list is the all vmid list
    if is_all:
        print 'is_all flag has been set'
        poweroff_vm=vm.power_off_all_vm(poweroff_login.spawn_child)
    ###### else judge index except
    else:
        print 'is_all flag has not been set'
        if is_except:
            ### Enable except, should poweroff the members in all list, occur 0 times in poweroff list
            print 'is_except flag has been set'
            for key,value in poweroff_vmname_dict.items():
                if value == 0:
                    poweroff_real_list.append(key)
        else:
        ### Disable except ,should poweroff the members in both in all list and poweroff list
            print 'is_except flag has been not set'
            for key,value in poweroff_vmname_dict.items():
                if value > 0:
                    poweroff_real_list.append(key)
        print 'Real poweroff vmname list is as below'
        print poweroff_real_list
        for poweroff_vmname in poweroff_real_list:
            ###power off the VM firstly
            ######change name to id
            poweroff_vmid=poweroff_login.vmname_to_vmid(poweroff_vmname,poweroff_login.spawn_child)
            poweroff_vm=poweroff_login.power_off_vm_via_vmid(poweroff_vmid,poweroff_login.spawn_child)
            print 'power off Virtual HiveOS %s successfully' % poweroff_vmid
    return poweroff_vm

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
    poweroff_vm_list=[]
    for vm_num in vm_list:
        if templefolder == 'VirtualOS_001':
            poweroff_vm_list.append('VirtualOS_%03d' % vm_num)
        else:
            poweroff_vm_list.append('%s%d' % (templename,vm_num))
    print 'power off vmname range is as below'
    print poweroff_vm_list
    poweroff_vm_result=poweroff_vm_via_list(host,user,password,poweroff_vm_list,is_except,is_all,is_debug)
    return poweroff_vm_result

if __name__=='__main__':
    try:
        poweroff_vm_result=main()
    except Exception,e:
        print str(e)
    else:
        if poweroff_vm_result:
            poweroff_vm_result.close(force=True)
            print 'power off all VMs successfully'
        else:
            print 'power off all VMs failed'