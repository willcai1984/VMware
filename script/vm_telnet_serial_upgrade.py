#!/usr/bin/env python
# Filename: ssh_ap_cmd.py
# Function: telnet target via serial and upgrade the version
# coding:utf-8
# Author: Well

from vm_telnet_serial import *
from vm_telnet_serial_reset import telnet_serial_reset
import argparse
parse = argparse.ArgumentParser(description='Upgrade VMs on Blade server')
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

parse.add_argument('-su', '--serveruser', required=False, default='root', dest='serveruser',
                    help='Image server user')

parse.add_argument('-sp', '--serverpassword', required=False, default='aerohive', dest='serverpassword',
                    help='Image server password')

parse.add_argument('-path', '--imagepath', required=True, dest='path',
                    help="Image path, for example '10.155.32.129:/home/qatest/cvg-ap-jan28.img' ")

parse.add_argument('-list', '--list', required=False, dest='portlist',
                    help='Configure serial port list')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-r', '--reset', required=False, action = 'store_true',dest='is_reset',
                    help='reset after upgrade')

def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    password=args.loginpassword
    loop_begin=args.loopbegin
    loop=args.loop
    server_user=args.serveruser
    server_password=args.serverpassword
    server_path=args.path
    is_reset = args.is_reset
    port_list_str=args.portlist
    is_debug=args.is_debug
    upgrade_command='save image scp://%s@%s' % (server_user,server_path)
    if is_reset: 
        command_list=[upgrade_command,'y',server_password,'reset config','y']
        expect_list=['image','password','Image upgrade success','configuration','System is rebooting']    
    else:
        command_list=[upgrade_command,'y',server_password,'reboot','y']
        expect_list=['image','password','Image upgrade success','want to reboot','System is rebooting']    
    commands_tuple_list=zip(command_list,expect_list)
    debug('list str is %s' % port_list_str, is_debug)
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
        ###logout stage is cannot use ctrl+q to leave login status, so we can use the have rebooting situation's code reset instead of cli
        telnet_serial_result=telnet_serial_reset(ip, user, password,commands_tuple_list, port, is_debug)
        if telnet_serial_result:
            pass
        else:
            return None
    return telnet_serial_result 

if __name__=='__main__':
    try:
        telnet_serial_cli_result=main()
    except Exception, e:
        print str(e)
    else:
        if telnet_serial_cli_result:
            telnet_serial_cli_result.close()
            print 'Telnet serail port upgrade successfully'
        else:
            print 'Telnet serail port upgrade failed'
    




