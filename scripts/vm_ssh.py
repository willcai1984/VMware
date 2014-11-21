#!/usr/bin/env python
# Filename: ssh_host.py
# Function: ssh tagert and execute cmds
# coding:utf-8
# Author: Well

import pexpect, re


###open debug or not
def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage

###modify a str such as 'x,x,x,x,x' or 'x,x-x,x,x,x-x' to list(mode is int)
def str_to_list(string, is_debug=False):
    input_list=string.split(',')
    str_list=[]
    for input_member in input_list:
        index1=re.search(r'[\D+]',input_member)
        index2=re.search(r'^\d+-\d+$',input_member)
        ###when index1 is None, match format'x'
        if index1==None:
            str_list.append(int(input_member))
        ###If index1 is Not None(True), need check index2, index2 should be True, match 'x-x' 
        elif index1 and index2:
            input_member_range_list=re.findall(r'\d+',input_member)
            ###need switch to int() before calculate
            input_member_range=int(input_member_range_list[1])-int(input_member_range_list[0])
            ###Judge if input_range is more than 0
            ######if equal to 0 add the member to the list 
            if input_member_range == 0:
                str_list.append(int(input_member_range_list[0]))
            ######if the range is >0 add the member in order
            elif input_member_range > 0:
                ###range() cannot cover the last one, so you need add 1 for the last
                for str_member in range(int(input_member_range_list[0]),int(input_member_range_list[1])+1):
                    ###primary mode is int, do not need switch 
                    str_list.append(int(str_member))
            else:
                print '''This parameter %s is not match format, the first member should less than the second ''' % input_member
                return None
        else:
            print '''This parameter %s is not match format, please enter correct format such as 'x,x,x' or 'x-x,x-x,x' ''' % input_member
            return None
    return str_list

### If the value >=0 means this list member is in the standard list occurs $value times in compare list
### Else means this list member is not in the standard occurs -$value times in compare list
def list_compare(list_standard,list_compare):
    dict_standard={}
    for standard_key in list_standard:
        dict_standard[standard_key]=0
    dict_compare={}
    for compare_key in list_compare:
        dict_compare[compare_key]=0
    for compare_member in list_compare:
        try:
            is_compare_member = dict_standard[compare_member]
        except KeyError:
            dict_compare[compare_member] = dict_compare[compare_member] - 1
        else:
            dict_standard[compare_member] = dict_standard[compare_member] + 1
    dict_extra={}
    for key,value in dict_compare.items():
        if value < 0:
            dict_extra[key]=value
    tuple_merger=dict_standard.items()+dict_extra.items()
    dict_merger=dict(tuple_merger)
    return dict_merger


class ssh_host:
    login_prompt='[$#>?]'
    def __init__(self, host, user, password, port=22):
        self.host=host
        self.user=user
        self.password=password
        self.port=port
    def login(self):
        ###be careful of the command format
        ssh_login_command='ssh %s@%s -p %s' % (self.user, self.host, self.port)
        login_password = self.password
        with open('ssh_login.txt', mode='w') as ssh_log_file_open:
            ssh_login_result=pexpect.spawn(ssh_login_command)
            ssh_login_result.logfile=ssh_log_file_open
            index=ssh_login_result.expect([pexpect.TIMEOUT, 'yes/no', '[Pp]assword'], timeout=20)    
            if index == 0:
                print '''TimeOut when send SSH Host'''
                ssh_login_result.close(force=True)
                return None 
            elif index == 1:
                print 'No auth confirm before, need send yes'
                ssh_login_result.sendline('yes')
                index=ssh_login_result.expect([pexpect.TIMEOUT, '[Pp]assword:'], timeout=20)
                if index == 0:
                    print '''TimeOut when send 'yes' confirm authenticity to login'''
                    ssh_login_result.close(force=True)
                    return None
            elif index == 2:
                print 'Already pass the auth, and get password'
            else:
                print '''Unknown error'''
                ssh_login_result.close(force=True)
                return None 
### Expect 'password', send password when the is detect is over
            print ssh_login_result.before,ssh_login_result.after
            ssh_login_result.sendline(login_password)
            print 'sending password'
###Use global variable need add class name  'ssh_host.login_prompt'
            index=ssh_login_result.expect([pexpect.TIMEOUT,'Aerohive.*%s' % ssh_host.login_prompt, ssh_host.login_prompt], timeout=20)
            if index==0:
                print '''TimeOut when send password to login Host'''
                ssh_login_result.close(force=True)
                return None 
            elif index==1:
                print '''Welcome to login Aerohive product'''
            elif index==2:
                print '''Welcome to general ssh host'''
            return ssh_login_result
    def login_execute_command(self, login_result_spawn_child, command_tuple_list):
###be careful, use self.login() not ssh_host.login(),because we should use the object's parameters 
        ssh_login_result=login_result_spawn_child
        cli_num=1
###func over means file open over, so we need open the log file again in every func
        with open('ssh_login.txt', mode='a') as ssh_log_file_open:
            ssh_login_result.logfile=ssh_log_file_open
            for cli,cli_expect in command_tuple_list:
                ssh_login_result.sendline(cli)
                index=ssh_login_result.expect([pexpect.TIMEOUT, cli_expect], timeout=10)
                if index == 0:
                    print '''TimeOut when execute the %d CLI entry, fail in Execute CLI parter''' % cli_num
                    print ssh_login_result.before, ssh_login_result.after
                    return None
                elif index == 1:
                    print '''Execute CLI '%s' successfully''' % cli
                cli_num += 1
        return ssh_login_result
    def login_exit(self, login_execute_command_result_spawn_child):
        ssh_login_result=login_execute_command_result_spawn_child
        with open('ssh_login.txt', mode='a') as ssh_log_file_open:
            ssh_login_result.logfile=ssh_log_file_open
            ssh_login_result.sendcontrol('d')
            ssh_login_result.expect('Connection.*closed')
            print 'Free SSH login successfully'
            return ssh_login_result

        