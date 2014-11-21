#!/usr/bin/env python
# path: /cw/
# Filename: telnet_serial_cli.py
# Function: telnet target via serial and execute CLI
# coding:utf-8
# Topo: LinuxPC-----L2sw-----(eth0)AP
# Author: Well
#Example command: python vm_telnet_serial_cli.py -d '10.155.32.106' -list '3' -f '/home/python/bin/config.txt'

from vm_telnet_serial import *
import argparse

parse = argparse.ArgumentParser(description='Delete VMs on Blade server')
###Cannot use -h, conflict with the help argument
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

parse.add_argument('-f', '--file', required=False, default='config.txt', dest='configfile',
                    help='Configure file name')

parse.add_argument('-list', '--list', required=False, dest='portlist',
                    help='Configure serial port list')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')


def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    password=args.loginpassword
    loop_begin=args.loopbegin
    loop=args.loop
    port_list_str=args.portlist
    configfile=args.configfile
    is_debug=args.is_debug
    ###Get configure command from file
    with open('%s' % configfile) as configure_open_file:
        configure_file_list=configure_open_file.readlines()
    commands_list=configure_file_list
    ###Cannot use dict, because dict is disorder, but our CLI should type in order    
    ###Generate command tuple, due to the command is read from file , '/n/r' may read into file, and our product meet '\n''s behavior is as below
    ######AH-1e9ac0#capwap client server name 10.155.32.114
    ######
    ######capwap client server name 10.155.32.114
    ######AH-1e9ac0#
    ######AH-1e9ac0#
    ######May generate two hostname+#, may cause next expect capture error, so delete'\n' and '\r' is one solution  
    ###\n=enter and sendline is with enter--->one command + 2 enters on Aerohive product--->two host name + two prompt
    commands_tuple_list = []
    for cli in commands_list:
        correct_cli=re.sub(r'[\n\r]','',cli)
        commands_tuple_list += [(correct_cli,'#')]
    ###Generate loop range, if enter port_list, need ignore -l and -lb, else, port_list may generate based on them
    debug('port list str is %s' % port_list_str, is_debug)
    if port_list_str:
        port_list=str_to_list(port_list_str)
    else:
        port_list=[]
        for i in range(loop):
            port=i+loop_begin
            port_list.append(port)
    debug('All ports list is as below', is_debug)
    debug(port_list, is_debug)
    for port in port_list:
        telnet_serial_result=telnet_serial_cli(ip, user, password,commands_tuple_list, port, is_debug)
        if telnet_serial_result:
            pass
        else:
            return None
    return telnet_serial_result

def telnet_serial_cli(ip, user, password, commands_tuple_list, port, is_debug):
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
    else:
        return None
    ###logout
    if serial_cli_result:
        serial_logout_result=serial_telnet.logout(serial_cli_result)
        debug('...................................................................',is_debug)
        debug('.................AerohiveOS %s CLI parter over.....................' % port,is_debug)
        debug('...................................................................',is_debug)
    else:
        return None 
    return serial_logout_result

if __name__ == '__main__':
    try:
        telnet_serial_cli_result=main()
    except Exception, e:
        print str(e)
    else:
        if telnet_serial_cli_result:
            telnet_serial_cli_result.close()
            print 'Telnet serail port execute cli successfully'
        else:
            print 'Telnet serail port execute cli failed'