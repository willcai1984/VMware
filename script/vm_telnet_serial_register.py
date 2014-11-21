#!/usr/bin/env python
# Filename: ssh_ap_cmd.py
# Function: telnet target via serial and upgrade the version
# coding:utf-8
# Author: Well
#Example command: python telnet_serial_clearsign.py -list '3-4' -debug

from telnet import telnet_login_via_serial,telnet_logout
from vm_ssh import str_to_list
import argparse, re, time, pexpect

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        print mesage

def telnet_serial_register(ip,serial,user,passwd,prompt,sn,timeout,is_debug):
    log_file_open=open('\home\test.txt', mode = 'w')
    spawn_child=telnet_login_via_serial(ip, serial, user, passwd, prompt, 2, 20, '\home\test.txt', log_file_open, is_debug)
    is_error=False
    is_successful=False
    spawn_child.sendline('wizard startup')
    debug("1 send 'wizard startup' successfully", is_debug)
    index=spawn_child.expect([pexpect.TIMEOUT,'Enter option .*:'],timeout=timeout)
    if index == 0:
        print "timeout when send 'wizard startup' to reactive CVG"
        is_error=True
    elif index == 1:
        spawn_child.sendline('2')
        debug("2 send '2' successfully", is_debug)
        index=spawn_child.expect([pexpect.TIMEOUT,'yes.*:'],timeout=timeout)
        if index == 0:
            print "timeout when send '2' to confirm not use http proxy"
            is_error=True
        elif index == 1:
            spawn_child.sendline('no')
            debug("3 send 'no' successfully", is_debug)
            index=spawn_child.expect([pexpect.TIMEOUT,'4 to 5 chars.*:'],timeout=timeout)
            if index == 0:
                print "timeout when send 'no' to confirm not use http proxy"
                is_error=True            
            elif index == 1:
                spawn_child.sendline('A3rO!5#')
                debug("4 send 'A3rO!5#' successfully", is_debug)
                index=spawn_child.expect([pexpect.TIMEOUT,'14 chars\):'],timeout=timeout)            
                if index == 0:
                    print "timeout when send 'A3rO!5#' to confirm active cvg"
                    is_error=True
                elif index == 1:
                    spawn_child.sendline(sn)
                    debug("5 send '%s' successfully" % sn, is_debug)
                    index=spawn_child.expect([pexpect.TIMEOUT,'changes.*yes.*:'],timeout=timeout)         
                    if index == 0:
                        print "timeout when send serial num %s to confirm active cvg" % sn
                        is_error=True
                    elif index == 1:
                        spawn_child.sendline('No')
                        debug("6 send 'No' successfully", is_debug)
                        index=spawn_child.expect([pexpect.TIMEOUT,prompt],timeout=timeout)
                        if index == 0:
                            print "timeout when send serial no to confirm not reboot the cvg"
                            is_error=True
                        elif index == 1:
                            is_successful=True
                            debug("6 meet prompt, can enter to logout process", is_debug)
    if is_successful:
        logout_result=telnet_logout(spawn_child,2, 20, True)
        if logout_result:
            return logout_result
            debug("logout successfully", is_debug)
        else:
            return None         
    if is_error:
        spawn_child.close(force=True)
        return None
                                                                                            
parse = argparse.ArgumentParser(description='Upgrade VMs on Blade server')
###Cannot use -h, conflict with the help argument

parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-m', '--prompt', required=False, default='AH-\w+#.*', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-l', '--loopnum', required=False, default=1, type=int,  dest='loop',
                    help='Loop times')                    

parse.add_argument('-lb', '--loopbegin', required=False, default=1, type=int, dest='loopbegin',
                    help='loop begin number')

parse.add_argument('-list', '--list', required=False, dest='portlist',
                    help='Configure serial port list')

parse.add_argument('-o', '--timeout', required=False, default=10,type=int, dest='timeout',
                    help='Time out value for every execute cli step')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')

def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.loginname
    passwd=args.loginpassword
    prompt=args.prompt
    timeout=args.timeout
    loop_begin=args.loopbegin
    loop=args.loop
    port_list_str=args.portlist
    is_debug=args.is_debug
    debug('list str is %s' % port_list_str, is_debug)
    if port_list_str:
        port_list=str_to_list(port_list_str)
    else:
        port_list=[]
        for i in range(loop):
            port=i+loop_begin
            port_list.append(port)
    debug('port list is as below %s' % str(port_list), is_debug) 
    serial_reg_list=[]
    for port in port_list:
        serial='2%s' % port
        sn='1234567890%04d' % int(port)  
        register_result=telnet_serial_register(ip,serial,user,passwd,prompt,sn,timeout,is_debug)
        if register_result:
            serial_reg_list.append((serial,1))
        else:
            serial_reg_list.append((serial,0))
    print serial_reg_list
    return register_result
    

if __name__=='__main__':
    try:
        telnet_serial_clearsign_result=main()
    except Exception, e:
        print str(e)
    else:
        if telnet_serial_clearsign_result:
            telnet_serial_clearsign_result.close()
            print 'Telnet serail port clear sign successfully'
        else:
            print 'Telnet serail port clear sign failed'