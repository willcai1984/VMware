#!/usr/bin/env python
# Filename: ssh_ap_cmd.py
# Function: telnet target via serial and upgrade the version
# coding:utf-8
# Author: Well
#Example command: python telnet_serial_clearsign.py -list '3-4' -debug

from vm_telnet_serial import *
import argparse

def clearsign_via_port(spwan_child,shell_pwd,is_debug):
    #shell password may not correct, so cannot use login_execute_command
    clearsign_login=spwan_child
    clearsign_login.sendline('_shell')
    clearsign_login.expect('password:')
    clearsign_login.sendline(shell_pwd)
    ###If the passwd is not correct,may meet password again
    ###cannot use '~$', this may means the last character is ~, and cannot use '$' too, need add \ for $, if not ,may match the end og the doc
    index=clearsign_login.expect(['password:','\$'])
    if index==0:
        ###meet wrong password status
        print 'Shell password is incorrect, please check!'
        ######should enter to normal status firstly,passwd can be tried 3 times
        clearsign_login.sendline(shell_pwd)
        clearsign_login.expect('password:')
        clearsign_login.sendline(shell_pwd)
        clearsign_login.expect('ERROR: Login incorrect.*#')
        debug('Enter to normal login status successfully',is_debug)
        return None
    elif index==1:
        print 'clear sign now'
        clearsign_login.sendline('/opt/ah/etc/ah_delete_sigfile')
        clearsign_login.expect('\$')
        print 'clear sign successfully'
        clearsign_login.sendcontrol('d')
        clearsign_login.expect('Welcome back to CLI console!.*#')
        debug('clear sign gui is as below',is_debug)
        debug(clearsign_login.after,is_debug)
    return clearsign_login

parse = argparse.ArgumentParser(description='Upgrade VMs on Blade server')
###Cannot use -h, conflict with the help argument

parse.add_argument('-u', '--user', required=False, default='admin', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-f', '--filepath', required=False, default='AP_Shell.xlsx',dest='filepath',
                    help="The xml file path you wan to read")

parse.add_argument('-c1', '--column1', required=False, default='0',dest='col1',
                    help="The xml file column 1 you want to get")

parse.add_argument('-c2', '--column2', required=False, default='2',dest='col2',
                    help="The xml file column 2 you want to get")

parse.add_argument('-c3', '--column3', required=False, default='3',dest='col3',
                    help="The xml file column 3 you want to get")

parse.add_argument('-sn', '--sheetnumber', required=False, default='0',dest='sheetnum',
                    help="The xml's sheet you want to get")

parse.add_argument('-list', '--list', required=False, dest='rowlist',
                    help='the xml row lists you want to read')

parse.add_argument('-debug', '--debug', required=False, action = 'store_true',dest='is_debug',
                    help='enable debug mode')

def main():
    args = parse.parse_args() 
    user=args.loginname
    password=args.loginpassword
    row_list_str=args.rowlist
    is_debug=args.is_debug    
    file_path=args.filepath
    ###get AP shell corresponding relationship
    col1=args.col1
    col2=args.col2
    col3=args.col3
    sheet_num=args.sheetnum
    ###switch to int mode(return APmode/serialinfo/ShellPassword)
    mode_serialinfo_shellpwd_list=read_xml_column_list(file_path,int(col1),int(col2),int(col3),int(sheet_num))
    row_list=str_to_list(row_list_str)
    ###get the real rows needed
    real_mode_serialinfo_shellpwd_list=[]
    for row in row_list:
        ###excel row start from 1 and the list start from 0, so need row-1
        real_mode_serialinfo_shellpwd_list.append(mode_serialinfo_shellpwd_list[row-1])
    ###split serialinfo to host and serial_port
    mode_host_port_shellpwd_list=[]
    for mode,serialinfo,shellpwd in real_mode_serialinfo_shellpwd_list:
        mode_host_port_shellpwd_list.append((mode,serialinfo.split(' ')[0],serialinfo.split(' ')[1],shellpwd))
    ###execute clearsign
    debug('The execute list info is as below',is_debug)
    debug(mode_host_port_shellpwd_list,is_debug)
    for mode,host,port,shellpwd in mode_host_port_shellpwd_list:
        ###Judge if the host is match the request
        is_host=re.search(r'^\d+.\d+.\d+.\d+$',host)
        is_port=re.search(r'^\d+$',port)
        is_shellpwd=re.search(r'^\w{16}$',shellpwd)
        if is_host and is_port and is_shellpwd:
            debug('%s %s %s %s %s %s' % (host,user,password,port,shellpwd,is_debug))
            debug('%s %s parter starts' % (host,port),is_debug)
            clearsign_telnet=telnet(host, user, password, is_debug, port)
            clearsign_login=clearsign_telnet.login()
            ###Judge if clearsign is login successfully
            ######if yes execute clear sign
            ######else can to next hoop
            if clearsign_login: 
                clearsign_result=clearsign_via_port(clearsign_login,shellpwd,is_debug)
                if clearsign_result:
                    clearsign_logout=clearsign_telnet.logout(clearsign_result)
                else:
                    debug('Clear sign failed',is_debug)
                    return None
            else:
                debug('Login failed',is_debug)
                return None
        else:
            if is_host == None:
                print 'The host %s not match the format' % host
                return None
            if is_port == None:
                print 'The serial port %s not match the format' % port
                return None
            if is_shellpwd == None:
                print 'The shell password %s not match the format' % shellpwd
                return None
    return clearsign_logout

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