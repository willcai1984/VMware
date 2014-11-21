#!/usr/bin/env python
# Filename: telnet_serial_get_info.py
# Function: telnet target via serial and execute CLI to get info you want
# coding:utf-8
# Author: Well

from vm_telnet_serial import *
import argparse

parse = argparse.ArgumentParser(description='Get info via regex in range')
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-l', '--loopnum', required=False, default=1, type=int,  dest='loop',
                    help='Loop times')                    

parse.add_argument('-lb', '--loopbegin', required=False, default=1, type=int, dest='loopbegin',
                    help='loop begin number')

parse.add_argument('-c', '--command', required=True,dest='command',
                    help='Command to execute')

parse.add_argument('-r', '--regEx', required=True,dest='reg',
                    help='regEx you want to get')

parse.add_argument('-list', '--list', required=False, dest='portlist',
                    help='Configure serial port list')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')

def telnet_serial_get():
### set telnet parameters
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    password=args.loginpassword
    loop_begin=args.loopbegin
    loop=args.loop
    command=args.command
    reg=args.reg
    port_list_str=args.portlist
    is_debug=args.is_debug
    ###Cannot use dict, the CLI should be enter in order
    commands_tuple_list=[(command,'#')]
    ###Generate loop range, if enter port_list, need ignore -l and -lb, else, port_list may generate based on them
    debug('list str is %s' % port_list_str, is_debug)
    if port_list_str:
        port_list=str_to_list(port_list_str)
    else:
        port_list=[]
        for i in range(loop):
            port=i+loop_begin
            port_list.append(port)
    get_list=[]
    for port in port_list:
        debug('...................................................................',is_debug)
        debug('.................AerohiveOS %s CLI parter begin....................' % port,is_debug)
        debug('...................................................................',is_debug)
        serial_num='2%03d' % port
        ###Set class
        serial_telnet=telnet(ip, user, password, is_debug, serial_num)
        ###Login
        serial_telnet_result=serial_telnet.login()
        ###Execute script
        ######if telnet result is None, return none
        if serial_telnet_result:
            debug('commads_tuple_list_is', is_debug)
            debug(commands_tuple_list, is_debug)
            serial_cli_result=serial_telnet.login_execute_command_via_list(commands_tuple_list, serial_telnet_result)
            debug('CLI execute process before is', is_debug)
            debug(serial_cli_result.before, is_debug)
            debug('CLI execute process after is', is_debug)
            debug(serial_cli_result.after, is_debug)
            get_member_list=re.findall(r'%s' % reg,serial_cli_result.before)
            try:
                get_member=get_member_list[0]
            except IndexError:
                print 'Cannot get info from %s CVG%s' % (ip,port)
            else:
                get_list.append((serial_num,get_member))
        else:
            return None
        ###logout
        ###logout
        if serial_cli_result:
            serial_logout_result=serial_telnet.logout(serial_cli_result)
            debug('...................................................................',is_debug)
            debug('.................AerohiveOS %s CLI parter over.....................' % port,is_debug)
            debug('...................................................................',is_debug)
        else:
            return None
    serial_logout_result.close()
    return get_list

if __name__ == '__main__':
    try:
        get_list=telnet_serial_get()
    except Exception, e:
        print str(e)
    else:
        if get_list:
            print get_list
        else:
            print 'Get info failed'
