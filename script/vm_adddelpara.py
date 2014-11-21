#!/usr/bin/env python
# Filename: adddelpara_vm.py
# Function: add or del parameters in vmx files
###Example command: 
###Add
###python adddelpara_vm.py -d '10.155.32.135' -tf 'Well_135_VirtualCVG_1' -list '2-3' -r 'test' 
###Del
###python adddelpara_vm.py -d '10.155.32.135' -tf 'Well_135_VirtualCVG_1' -list '2-3' -r 'test' -a 'del'
# coding:utf-8
# Author: Well
from vm import *
import argparse

def add_del_para_vm(spawn_child,add_del_para,path_name,is_debug,action):
    add_del_login=spawn_child
    ###Enter to correct path
    show_vm_command='cat %s' % path_name
    add_del_login.sendline(show_vm_command)
    add_del_login.expect('#')
    add_del_file=add_del_login.before
    ###delete cat command and the end login prompt
    ######Start part, may has the command cat ***
    ######End part, may has the prompts(~),(the last one has no '\r\n',if add this place, may cause split has '' in the last)
    ######The originate file every line has '\r\n' (include the last line),so we should follow it
    add_del_result='\r\n'.join(add_del_file.split('\r\n')[1:-1])
    ###Judge the action mode
    if action == 'add':
        ###add the parameters
        debug('add mode is set, executing add process',is_debug)
        add_del_result = add_del_result + '\r\n' + add_del_para
    elif action == 'del':
        ###delete the lines, should delete'\r\n' together
        debug('del mode is set, executing del process',is_debug)
        debug('''The file's parameters is as below''',is_debug)
        debug(add_del_result,is_debug)
        ###consider the first one will not be deleted, and the most probability is deleted the last one, so put the '\r\n' before the para
        add_del_para='\r\n'+add_del_para
        add_del_result = re.sub(add_del_para,'',add_del_result)
    else:
        print 'Action error, only support add or del'
    vmx_parameters_list=add_del_result.split('\r\n')
    debug('New vmx file is as below',is_debug)
    debug(vmx_parameters_list,is_debug)
    ###for the firt should use '>' the other use '>>'
    for vmx_id in range(len(vmx_parameters_list)):
        if vmx_id == 0:
            add_del_login.sendline('''echo '%s' > %s''' % (vmx_parameters_list[vmx_id],path_name))
            add_del_login.expect('#')
#        elif vmx_id == len(vmx_parameters_list) - 1:
#            ###The originate file every line has '\r\n' (include the last line),so we should follow it!!be careful
#            add_del_login.sendline('''echo -n '%s' >> %s''' % (vmx_parameters_list[vmx_id],path_name))
#            add_del_login.expect('#')
        else:
            add_del_login.sendline('''echo '%s' >> %s''' % (vmx_parameters_list[vmx_id],path_name))
            add_del_login.expect('#')
    return add_del_login

parse = argparse.ArgumentParser(description='add')
###Cannot use -h, conflict with the help argument
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='root', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-tf', '--templefolder', required=False, default='VirtualOS_001',  dest='templefolder',
                    help='Temple folder name')

parse.add_argument('-list', '--list', required=False, dest='vmlist',
                    help='Configure vm list')

parse.add_argument('-debug', '--debug', required=False,default=False,action = 'store_true',dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-r', '--regex', required=False, default=False, dest='reg',
                    help='The regex you want to find')

parse.add_argument('-a', '--action', required=False, default='add', dest='action',choices=['add','del'],
                    help='The action you want to execute, add or del')


def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    password=args.loginpassword
    vm_list_str=args.vmlist
    is_debug=args.is_debug
    templefolder=args.templefolder
    templename=re.sub(r'\d+$','',templefolder)
    add_del_para=args.reg
    action=args.action
    vm_list=str_to_list(vm_list_str)
    vm_name_list=[]
    add_del_login=vm(ip,user,password)
    if templefolder=='VirtualOS_001':
        for vm_num in vm_list:
            vm_name_list.append(templename+'%03d' % vm_num)
    else:
        for vm_num in vm_list:
            vm_name_list.append(templename+'%d' % vm_num)
    debug('The vm in bleow list will be operated soon', is_debug)
    debug(vm_name_list,is_debug)
    for vm_name in vm_name_list:
        add_del_file_path='vmfs/volumes/datastore1/'+vm_name+'/'+templefolder+'.vmx'
        debug(add_del_file_path,is_debug)
        add_del_vm_result=add_del_para_vm(add_del_login.spawn_child,add_del_para,add_del_file_path,is_debug,action)
        if add_del_vm_result:
            debug('vm %s add_del successfully' % vm_name,is_debug)
        else:
            debug('vm %s add_del failed' % vm_name,is_debug)
            return None
    return add_del_vm_result

if __name__=='__main__':
    add_del_result=main()
    if add_del_result:
        add_del_result.close()
        print 'add_del successfully'
    else:
        print 'add_del failed'
    