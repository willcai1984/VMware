#!/usr/bin/env python
# Filename: subpara_vm.py
# Function: sub parameters in vmx files
###Example command: python subpara_vm.py -d '10.155.32.135' -tf 'Well_135_VirtualCVG_1' -list '2-3' -r 'ethernet0.networkName = "\w+"' -s 'ethernet0.networkName = "L3_H3C_135"'
# coding:utf-8
# Author: Well
from vm import *
import argparse

def sub_para_vm(spawn_child,sub_from,sub_to,path_name,is_debug):
    sub_login=spawn_child
    ###Enter to correct path
    show_vm_command='cat %s' % path_name
    sub_login.sendline(show_vm_command)
    sub_login.expect('#')
    sub_file=sub_login.before
    ###delete cat command and the end login prompt
    ######Start part, may has the command cat ***
    ######End part, may has the prompts(~),(the last one has no '\r\n',if add this place, may cause split has '' in the last)
    ######Use '\r\n' for split
    sub_result='\r\n'.join(sub_file.split('\r\n')[1:-1])
    ###search sub_file and judge if the sub_from in the sub_file
    ###sub the lines
    ###search sub_file and judge if the sub_from in the sub_file
    sub_search_result=re.search(r'%s' % sub_from,sub_result)
    if sub_search_result:
        sub_result=re.sub(r'%s' % sub_from,sub_to,sub_result)
    else:
        return None
#    ###write the file to vmx
#    ######add '\r\n' to the end first
#    sub_result+='\r\n'
#    ###first solution complete the script in shell via bash(echo > file)
#    ######here we should process the shell_command, due to the print value is 'enter' when the var value is '\r\n', sub '\r\n' to '\\r\\n' 
#    sub_result=re.sub(r'\r\n',r'\\r\\n',sub_result)
#    print sub_result
#    ######vmware can only support echo 1023 characters...so should resolve this issue firstly, and may consider the 1023 limit may Separate '\r\n'
#    sub_login.sendline('''echo -e '%s' > %s''' % (sub_result,path_name))
#    sub_login.expect('#')
    ### other solution,split file to lines(echo every lines and add to the file,no need to add '\r\n')
    vmx_parameters_list=sub_result.split('\r\n')
    debug('New vmx file is as below',is_debug)
    debug(vmx_parameters_list,is_debug)
    ###for the firt should use '>' the other use '>>'
    for vmx_id in range(len(vmx_parameters_list)):
        if vmx_id == 0:
            sub_login.sendline('''echo '%s' > %s''' % (vmx_parameters_list[vmx_id],path_name))
            sub_login.expect('#')
        else:
            sub_login.sendline('''echo '%s' >> %s''' % (vmx_parameters_list[vmx_id],path_name))
            sub_login.expect('#')
    return sub_login

parse = argparse.ArgumentParser(description='Use reg to find the target and sub it')
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

parse.add_argument('-s', '--sub', required=False, default=False, dest='sub',
                    help='The parameter you want to sub to')


def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    password=args.loginpassword
    vm_list_str=args.vmlist
    is_debug=args.is_debug
    templefolder=args.templefolder
    templename=re.sub(r'\d+$','',templefolder)
    sub_from=args.reg
    sub_to=args.sub
    vm_list=str_to_list(vm_list_str)
    vm_name_list=[]
    sub_login=vm(ip,user,password)
    if templefolder=='VirtualOS_001':
        for vm_num in vm_list:
            vm_name_list.append(templename+'%03d' % vm_num)
    else:
        for vm_num in vm_list:
            vm_name_list.append(templename+'%d' % vm_num)
    debug('The vm in bleow list will be operated soon',is_debug)
    debug(vm_name_list,is_debug)
    for vm_name in vm_name_list:
        sub_file_path='vmfs/volumes/datastore1/'+vm_name+'/'+templefolder+'.vmx'
        debug(sub_file_path,is_debug)
        sub_vm_result=sub_para_vm(sub_login.spawn_child,sub_from,sub_to,sub_file_path,is_debug)
        if sub_vm_result:
            debug('vm %s sub successfully' % vm_name,is_debug)
        else:
            debug('vm %s sub failed' % vm_name,is_debug)
            return None
    return sub_vm_result

if __name__=='__main__':
    sub_result=main()
    if sub_result:
        sub_result.close()
        print 'sub successfully'
    else:
        print 'sub failed'
    