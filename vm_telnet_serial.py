#!/usr/bin/env python
# Filename: telnet_serial.py
# Function: define all telnet used function
# coding:utf-8
# Author: Well
###telnet_class=a=telnet('10.155.32.106','admin','aerohive',True,'2003') 
import pexpect, os, re, sys, xlrd

###open debug or not
def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage

###modify a str such as 'x,x,x,x,x' or 'x,x-x,x,x,x-x' to list
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


###def a func to read xml and return list what cols you care, [(col1[0],col2[0],col3[0]),(col1[1],col2[1],col3[1])...]
def read_xml_column_list(file_path,col1,col2=-1,col3=-1,sheet_num=0):
    data = xlrd.open_workbook('%s' % file_path)
    print 'get date successfully'
    sheet = data.sheets()[int(sheet_num)]
    print 'get sheet successfully'
    ###get the total row num
    nrow = sheet.nrows
    print 'get total row number successfully'
    print nrow
    xml_list=[]
    ###Judge col2, don't care when col2<0 and col3>0
    if col2>=0:
        ###Judge col3
        if col3>=0:
            ###col1 col2 col3
            for row_num in range(nrow):
                xml_list.append((sheet.col(int(col1))[row_num].value,sheet.col(int(col2))[row_num].value,sheet.col(int(col3))[row_num].value))
        else:
            ###col1 col2
            for row_num in range(nrow):
                xml_list.append((sheet.col(int(col1))[row_num].value,sheet.col(int(col2))[row_num].value))
    else:
        ###col1
        for row_num in range(nrow):
            xml_list.append(sheet.col(int(col1))[row_num].value)
    return xml_list


class telnet:
    def __init__(self, host, user, password, is_debug=False, serial_num='', log_file='telnet_login.txt', login_prompt='[$#>?]'):
        self.host=host
        self.user=user
        self.password=password
        self.is_debug=is_debug
        ### if serial is '' ,cannot be int()
        if serial_num:
            self.serial_num=int(serial_num)
        else:
            self.serial_num=serial_num
        self.log_file=log_file
        self.login_prompt=login_prompt
        self.log_file_open=open(log_file, mode = 'w')
        print 'Telnet process start, init parameters............'
    def __del__(self):
        self.log_file_open.close()
        print 'Telnet process over.' 
    def login(self):
        host=self.host
        user=self.user
        password=self.password
        serial_num=self.serial_num
        is_debug=self.is_debug
        ###Judge if serial_num is null
        if serial_num:
            telnet_login_command='telnet %s %s' % (host,serial_num)
        else:
            telnet_login_command='telnet %s' % (host)
        debug('''Telnet login command is "%s"''' % telnet_login_command, is_debug)
        telnet_login_result=pexpect.spawn(telnet_login_command)
        telnet_login_result.logfile=self.log_file_open
        debug('Step1 send telnet command successfully', is_debug)
        index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Escape character is','Unable .* Connection refused','[Pp]assword'], timeout=20)
        if index  == 0:
            print 'TimeOut when telnet the target, fail in step 1' 
            print telnet_login_result.before, telnet_login_result.after
            telnet_login_result.close(force=True)
            return None
            ###Judge if we cannot reach the host, we cannot judge the serial port is alive or not(all match escape first, we can only judge it after escape)
        elif index == 1:
            print 'No route to the host, please check your network and confirm you can reach the host %s' % host
            telnet_login_result.close(force=True)
            return None
            ###Meet key words 'Escape character is' maybe 2 status, one is login successfully but the other is the console port is in using or not valid        
        elif index == 3:
            print 'telnet: Unable to connect to remote host: Connection refused, please confirm the serial num %s is alive' % serial_num
            telnet_login_result.close(force=True)
            return None
        elif index == 2:
            debug('....................Step 2....................',is_debug)
            telnet_login_result.sendline('')
            debug('''Step2 send 'Enter' to confirm login''',is_debug)
            ###may meet aerohive pruduct powerdown on vmwarw ---EOF
            ###aerohive product login---login
            ###aerohive product already login---#
            ###aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
            ###Cisco product the second time password(because the first is at the same time of the 'Escape character is', cannot be matched)
            ###If the cisco serial server's port connect nothing, would stay'Escape character is '^]'.' when you send 'enter', cannot diff it from the normal way ,use timeout to mark it
            index = telnet_login_result.expect([pexpect.EOF, pexpect.TIMEOUT, 'login', self.login_prompt,'Use the Aerohive.*<yes|no>:','[Pp]assword'], timeout=5)
            if index == 0:
                print 'The serial num %s not exist, please check' % serial_num
                telnet_login_result.close(force=True)
                return None
            ###if we enter a not alive serial port on serial server, may meet send enter no reply
            elif index == 1:
                print '''TimeOut when send 'Enter' to confirm login or the serial port is no alive, fail in step 2'''
                telnet_login_result.close(force=True)
                return None
            elif index == 2:
                debug('....................Step 3....................',is_debug)
                telnet_login_result.sendline(user)
                debug('''Step3 send user name '%s' to confirm login''' % user, is_debug)
                index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=10)
                if index == 0:
                    print '''TimeOut when send user name to confirm login, fail in step 3''' 
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('....................Step 4....................',is_debug)
                    telnet_login_result.sendline(password)
                    debug('''Step4 send password to confirm login''',is_debug)
                    ###may meet 'Use the Aerohive Initial Configuration Wizard? <yes|no>' if you is the first time to login the AP after reset
                    ###this place index1 cannot use loginprompt, because index3 include ? and > ,use # instead 
                    index = telnet_login_result.expect([pexpect.TIMEOUT, '#', 'Use the Aerohive.*<yes|no>:'], timeout=10)
                    if index == 0:
                        print '''TimeOut when send password to confirm login, fail in step 4''' 
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        debug('....................Step 5....................',is_debug)
                        debug('Step 5 send password and login successfully, could execute CLI now',is_debug)
                    elif index == 2:
                        telnet_login_result.sendline('no')
                        index = telnet_login_result.expect([pexpect.TIMEOUT, self.login_prompt],timeout=10)
                        if index == 0:
                            print '''TimeOut when send no to not init by default configure, fail in step 5''' 
                            telnet_login_result.close(force=True)
                            return None
                        elif index == 1:
                            debug('....................Step 6....................',is_debug)
                            debug('''Step 6 meet reset configure info and send no to not init by default,could execute CLI now ''',is_debug)
            elif index == 3:
                debug('Step 2 Login successfully already and execute CLI',is_debug)
            elif index == 4:
                debug('Step 2 meet reset configure info and send no to not init by default',is_debug)
                telnet_login_result.sendline('no')
                index = telnet_login_result.expect([pexpect.TIMEOUT, self.login_prompt],timeout=10)
                if index == 0:
                    print '''TimeOut when send no to not init by default configure, fail in step 2''' 
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('....................Step 3....................',is_debug)
                    debug('''Step 3 send no to not init by default successfully ,could execute CLI now ''',is_debug)
            elif index == 5:
                print 'Welcome to serial server'
                ###need use expect to cut the cache(two password)
                telnet_login_result.expect('[Pp]assword')
                telnet_login_result.sendline(password)
                debug('''Step2 send password to confirm login''',is_debug)
                index = telnet_login_result.expect([pexpect.TIMEOUT, self.login_prompt], timeout=10)
                if index == 0:
                    print '''TimeOut when send password to confirm login, fail in step 2''' 
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('....................Step 3....................',is_debug)
                    debug('Step 3 Login successfully and execute CLI',is_debug)
        print 'Login %s %s successfully' % (host, serial_num)
        return telnet_login_result     
    ###commands_dict should be your execute CLI and expexct value
    def login_execute_command_via_list(self,commands_tuple_list,spawn_child):
        is_debug=self.is_debug
        telnet_login_result=spawn_child
        cli_num=1
        for cli,cli_expect in commands_tuple_list:
            telnet_login_result.sendline(cli)
            index=telnet_login_result.expect([pexpect.TIMEOUT, cli_expect], timeout=10)
            if index == 0:
                print '''TimeOut when execute the %d CLI entry, fail in Execute CLI parter''' % cli_num
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                #debug info should add in class not other py, especially for loog part
                debug('''Execute CLI '%s' ''' % cli,is_debug)
                debug('''CLI '%s' execute process before is''' % cli, is_debug)
                debug(telnet_login_result.before, is_debug)
                debug('''CLI '%s' execute process after is''' % cli, is_debug)
                debug(telnet_login_result.after, is_debug)
        return telnet_login_result
    def login_execute_command(self,cli,cli_expect,spawn_child):
        is_debug=self.is_debug
        telnet_login_result=spawn_child
        telnet_login_result.sendline(cli)
        index=telnet_login_result.expect([pexpect.TIMEOUT, cli_expect], timeout=10)
        if index == 0:
            print '''TimeOut when execute CLI, fail in Execute CLI parter'''
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            debug('%s' % cli,is_debug)
        return telnet_login_result
    def logout(self,spawn_child):
        telnet_login_result=spawn_child
        print '....................Quit login status....................'
        ###Aerohive and Cisco's behavior is not the same for sending ctrl+d,cisco is no reply, so send enter for detail check
        telnet_login_result.sendcontrol('d')
        telnet_login_result.sendline('')
        index=telnet_login_result.expect(['login',self.login_prompt])
        ###ctrl+d + enter, aerohive product will generate two login:
        ###ctrl+d +enter,cisco product will generate hostname+login prompt
        if index == 0:
            debug('Quit Aerohive products logining status successfully')
        if index == 1:
            debug('Cisco products, sending ctrl+d directly')
        print '....................Free serial port....................'
        telnet_login_result.sendcontrol(']')
        telnet_login_result.expect('telnet')
        telnet_login_result.sendline('quit')
        telnet_login_result.expect('Connection closed')
        print 'Free %s %s successfully' % (self.host,self.serial_num)
        return telnet_login_result