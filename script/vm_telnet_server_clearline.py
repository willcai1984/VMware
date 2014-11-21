#!/usr/bin/env python
# Filename: telnet_serial_clearline.py
# Function: telnet serial server and clear all lines
# coding:utf-8
# Author: Well
###Example command:python telnet_serial_clearline.py -d '10.155.32.106' -list '1-3,5,9-13'
from vm_telnet_serial import *
import argparse
parse = argparse.ArgumentParser(description='clear serial server lines')
###Cannot use -h, conflict with the help argument
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-list', '--list', required=False, dest='portlist',
                    help='Configure serial port list')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-e', '--except', required=False, default=False, dest='is_except', action = 'store_true',
                    help='Enable except mode, all VMs except your set range will be deleted')

parse.add_argument('-a', '--all', required=False, default=False, dest='is_all', action = 'store_true',
                    help='Enable all mode, all VMs will be powered on')

def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    password=args.loginpassword
    port_list_str=args.portlist
    port_list=str_to_list(port_list_str)
    is_debug=args.is_debug
    is_all=args.is_all
    is_except=args.is_except
    debug(port_list,is_debug)
    telnet_server_clearline_result=telnet_server_clearline(ip, user, password, port_list, is_debug, is_all, is_except)
    return telnet_server_clearline_result

def telnet_server_clearline(ip, user, password, port_list, is_debug, is_all, is_except):
    debug('Start login serial server')
    
    server_telnet=telnet(ip, user, password, is_debug)
    server_login=server_telnet.login()
    ###enable console firstly
    debug('Enable console', is_debug)
    enable_list=[('enable','[Pp]assword'),(password,'#')]
    server_enable=server_telnet.login_execute_command_via_list(enable_list,server_login)
    ###get all lines info
    server_enable.sendline('show line')
    ### cannot be shown in a page may meet 'more'
    index=server_enable.expect(['#','--More--'])
    all_line_file=server_enable.before
    ###send enter till match '#'
    while index:
        server_enable.sendline('')
        index=server_enable.expect(['#','--More--'])
        debug('All lines file is as below', is_debug)
        debug(server_enable.before,is_debug)
        ###for get the whole 'show line' log, all_line_file+
        ###findall from str, the parameters are str, need swtich to int
        all_line_file+=server_enable.before
        all_line_str_list=re.findall(r'(\d+) +[A-Z][A-Z][A-Z] + \d+/\d+', all_line_file)
        all_line_list=[]
        for line_str in all_line_str_list:
            all_line_list.append(int(line_str))
        debug('All lines list is as below', is_debug)
        debug(all_line_list, is_debug)
        
    ###Generate real_line_list
    ######Judge if is_all set, is yes, ignore other parameters   
    if is_all:
        debug('is_all flag set to yes, ignore other parameters')    
        real_line_list=all_line_list
    ###not set is_all,judge is_except     
    else:
        debug('is_all flag not, judge is_except') 
        ###Judge if is_except set
        real_line_list=[]
        line_dict=list_compare(all_line_list, port_list)
        debug(line_dict,is_debug)
        ###is_except is set, choose in the all_line_list but not in port_list' member, value == 0
        if is_except:
            for key,value in line_dict.items():
                if value == 0:
                    real_line_list.append(key)
        ###is_except is set, choose both in the all_line_list and port_list' member, value > 0        
        else:
            for key,value in line_dict.items():
                if value > 0:
                    real_line_list.append(key)
    debug(real_line_list)
    ###Clear line process            
    for line in real_line_list:
        clear_list=[('clear line %s' % line,'confirm]'),('','#')]
        #spawn update all the time, so you can use any of them
        server_clear=server_telnet.login_execute_command_via_list(clear_list,server_login)
    return server_clear

if __name__=='__main__':
    try:
        clear_line_result = main()
    except Exception,e:
        print 'The error info is as below'
        print str(e)
    else:
        if clear_line_result:
            print 'clear all lines successfully'
            clear_line_result.close()
        else:
            print 'clear lines failed'