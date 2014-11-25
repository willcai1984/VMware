  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import pexpect, sys, re
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

from args import ExpectArgs
from unit import sleep, debug, info, warn, error, str2list, generate_cli_mode_expect_timeout_wait_list

class Expect(object):
    def __init__(self):
        self.args = ExpectArgs()
        self.mode = self.args.mode
        self.ip = self.args.ip
        self.port = self.args.port
        self.user = self.args.user
        self.passwd = self.args.passwd
        self.prompt = self.args.prompt
        self.timeout = self.args.timeout
        self.log_file = self.args.log_file
        self.cli_list = self.args.cli_list
        self.config_file = self.args.config_file
        self.wait = self.args.wait
        self.retry = self.args.retry
        self.para_dict = self.args.para_dict
        self.debug_level = self.args.debug_level
        self.child = None
        self._debug()
        self._tag()
        self._cli()
        self._port()
        self._logfile_init()
        # use str(self) to print __str__ value
        info('Expect Args\n' + str(self), self.is_info)

    def __del__(self):
        if self.child:
            self.child.close(force=True)
        if self.f_o:
            self._logfile_process()

    def __str__(self):
        s = []
        s.append('Mode        = %s' % self.mode)
        s.append('IP          = %s' % self.ip)
        s.append('Port        = %s' % self.ip)
        s.append('User        = %s' % self.user)
        s.append('Passwd      = %s' % self.passwd)
        s.append('Prompt      = %s' % self.prompt)
        s.append('Timeout     = %s' % self.timeout)
        s.append('Log_file    = %s' % self.log_file)
        for i in self.cli_list:
            s.append('CLI         = %s' % i)
        s.append('Config_file = %s' % self.config_file)
        s.append('Wait        = %s' % self.wait)
        s.append('Retry       = %s' % self.retry)
        s.append('PARA_Dict   = %s' % str(self.para_dict))
        s.append('Debug_level = %s' % self.debug_level)
        return '\n'.join(s)

    def ssh_login(self):
        info('''[LOGIN-SSH]Send cli to login target''', self.is_info)
        self._retry_not_expect('ssh %s@%s -p %s' % (self.user, self.ip, self.port) , 'sendline', [pexpect.TIMEOUT, 'Connection timed out|No route to host.*', 'continue connecting .*\?', '[Pp]assword:', self.prompt])
        if self.log_file == 'stdout':
            self.child.logfile_read = sys.stdout
        else:
            self.child.logfile_read = self.f_o
        # maybe we can add retry in index 0 and 1
        if self.exec_index == 0:
            self.is_error = True
            info('''[LOGIN-SSH]From 'SSH CMD' jump to is_error, Timeout''', self.is_info)
        elif self.exec_index == 1:
            self.is_error = True
            info('''[LOGIN-SSH]From 'SSH CMD' jump to is_error, Timeout/NoRoute''', self.is_info)
        elif self.exec_index == 2:
            info('''[LOGIN-SSH]The target is not in known host list, need send yes to confirm login''', self.is_info)
            self._retry_not_expect('yes', 'sendline', [pexpect.TIMEOUT, '[Pp]assword:', self.prompt])
            if self.exec_index == 0:
                self.is_error = True
                info('''[LOGIN-SSH]From 'YES Confirm' jump to is_error, Timeout''', self.is_info)
            elif self.exec_index == 1:
                info('''[LOGIN-SSH]Send 'YES Confirm' successfully, meet passwd''', self.is_info)
                self.is_passwd = True
                info('''From 'YES Confirm' jump to is_passwd''', self.is_info)
            elif self.exec_index == 2:
                info('''[LOGIN-SSH]Send 'YES Confirm' successfully, meet prompt''', self.is_info)
                self.is_prompt = True
                info('''From 'YES Confirm' jump to is_prompt''', self.is_info)
        elif self.exec_index == 3:
            self.is_passwd = True
            info('''[LOGIN-SSH]From 'SSH CMD' jump to is_passwd''', self.is_info)
        elif self.exec_index == 4:
            self.is_prompt = True
            info('''[LOGIN-SSH]From 'SSH CMD' jump to is_prompt''', self.is_info)
        else:
            info('''[LOGIN-SSH]Cannot match any option in expect list''', self.is_info)
            self.is_error = True
            info('''[LOGIN-SSH]From 'SSH CMD' jump to is_error, Unknow error''', self.is_info)
        self._basic_login()

    def telnet_login(self):
        info('''[LOGIN-TELNET]Send cli to login target''', self.is_info)
        self._retry_not_expect('telnet %s %s' % (self.ip, self.port) , 'sendline', [pexpect.TIMEOUT, 'No route to host.*', 'Unable .* Connection refused.*', 'Escape character is.*'])
        if self.log_file == 'stdout':
            self.child.logfile_read = sys.stdout
        else:
            self.child.logfile_read = self.f_o
        
        # maybe we can add retry in index 0 and 1
        if self.exec_index == 0:
            self.is_error = True
            info('''[LOGIN-TELNET]From 'TELNET CMD' jump to is_error, Timeout''', self.is_info)
        elif self.exec_index == 1:
            self.is_error = True
            info('''[LOGIN-TELNET]From 'TELNET CMD' jump to is_error, NoRoute''', self.is_info)
        elif self.exec_index == 2:
            self.is_error = True
            info('''[LOGIN-TELNET]From 'TELNET CMD' jump to is_error, ConnectRefused''', self.is_info)
        elif self.exec_index == 3:
            info('''[LOGIN-TELNET]Send 'TELNET CMD' successfully, meet Escape''', self.is_info)
            self._retry_not_expect('' , 'sendline', [pexpect.TIMEOUT, pexpect.EOF, 'login.*', '[Pp]assword.*', 'yes\|no>:.*', self.prompt])
            if self.exec_index == 0:
                self.is_error = True
                info('''[LOGIN-TELNET]From 'Enter' jump to is_error, Timeout''', self.is_info)
            elif self.exec_index == 1:
                self.is_error = True
                info('''[LOGIN-TELNET]From 'Enter' jump to is_error, VMOSInActive''', self.is_info)
            elif self.exec_index == 2:
                self.is_user = True
                info('''[LOGIN-TELNET]From 'Enter' jump to is_user''', self.is_info)
            elif self.exec_index == 3:
                self.is_passwd = True
                info('''[LOGIN-TELNET]From 'Enter' jump to is_passwd''', self.is_info)
            elif self.exec_index == 4:
                self.is_no = True
                info('''[LOGIN-TELNET]From 'Enter' jump to is_no''', self.is_info)
            elif self.exec_index == 5:
                self.is_prompt = True
                info('''[LOGIN-TELNET]From 'Enter' jump to is_prompt''', self.is_info)
        else:
            info('''[LOGIN-TELNET]Cannot match any option in expect list''', self.is_info)
            self.is_error = True
            info('''[LOGIN-TELNET]From 'TELNET CMD' jump to is_error, Unknow error''', self.is_info)
        self._basic_login()

    def _basic_login(self):
        # default is retry 5 times and the interval is 5s
        if self.is_user:
            info('[LOGIN-USER]Meet user,send user to confirm login', self.is_info)
            self._retry_not_expect(self.user, 'sendline', [pexpect.TIMEOUT, '[Pp]assword.*'])
            if self.exec_index == 0:
                self.is_error = True
                info('''[LOGIN-USER]Send username cannot get passwd, Timeout''', self.is_info)
                info('''[LOGIN-USER]From is_user jump to is_error''', self.is_info)
            elif self.exec_index == 1:                  
                self.is_passwd = True
                info('''[LOGIN-USER]From is_user jump to is_passwd''', self.is_info)
        
        if self.is_passwd:
            info('[LOGIN-PASSWD]Meet passwd,send passwd to confirm login', self.is_info)
            self._retry_not_expect(self.passwd, 'sendline', [pexpect.TIMEOUT, '\nlogin.*', '[Pp]assword.*', 'yes\|no>:.*', self.prompt])
            if self.exec_index == 0:
                self.is_error = True
                info('''[LOGIN-PASSWD]Send passwd cannot get expect, Timeout''', self.is_info)
                info('''[LOGIN-PASSWD]From is_passwd jump to is_error''', self.is_info)
            elif self.exec_index == 1:
                self.is_error = True
                info('''[LOGIN-PASSWD]Send passwd, meet user again, may wrong user or passwd''', self.is_info)
                info('''[LOGIN-PASSWD]From is_passwd jump to is_error''', self.is_info)
            elif self.exec_index == 2:
                self.is_error = True
                info('''[LOGIN-PASSWD]Send passwd, meet passwd again, may wrong user or passwd''', self.is_info)
                info('''[LOGIN-PASSWD]From is_passwd jump to is_error''', self.is_info)                         
            elif self.exec_index == 3:
                self.is_no = True
                info('''[LOGIN-PASSWD]From is_passwd jump to is_no process ''', self.is_info)
            elif self.exec_index == 4:
                self.is_prompt = True
                info('''[LOGIN-PASSWD]From is_passwd jump to is_prompt process ''', self.is_info)
        
        if self.is_no:
            info('[LOGIN-NO]Meet yes or no,send no to not use default config', self.is_info)
            self._retry_not_expect('no', 'sendline', [pexpect.TIMEOUT, self.prompt])         
            if self.exec_index == 0:
                self.is_error = True
                info('''[LOGIN-NO]Send no cannot get prompt, Timeout''', self.is_info)
                info('''[LOGIN-NO]From is_no jump to is_error''', self.is_info)
            elif self.exec_index == 1:
                self.is_prompt = True
                info('''[LOGIN-NO]From is_no jump to is_prompt''', self.is_info)
        
        if self.is_prompt:
            info('''[LOGIN-PROMPT]Meet prompt, can execute cli now''', self.is_info)
        
        if self.is_error:
            info('''[LOGIN-ERROR]Meet error, close the child''', self.is_info)
            info('''[LOGIN-ERROR]BEFORE is: %s''' % self.child.before, self.is_info)
            info('''[LOGIN-ERROR]AFTER is : %s''' % self.child.after, self.is_info)
            raise ValueError, '''Login Error'''

    def basic_exec(self):
        for cli, mode, expect, timeout, wait in self.c_m_e_t_w_list:
            exec_cli = '''self.child.%s(cli)''' % mode
            exec(exec_cli)
            exec_index = self.child.expect([pexpect.TIMEOUT, expect, '--More--', 'More:', '-- More --'], timeout)
            if exec_index == 0:
                info('''[CLI]Meet Timeout''', self.is_info)
                info('''[CLI]CLI    = %s''' % cli, self.is_info)
                info('''[CLI]Expect = %s''' % expect, self.is_info)
                info('''[CLI]Before = %s''' % self.child.before, self.is_info)
                info('''[CLI]After  = %s''' % self.child.after, self.is_info)    
            elif exec_index == 1:
                info('''[CLI]Successfully Execute "%s"''' % cli, self.is_info)
            elif exec_index == 2 or exec_index == 3 or exec_index == 4:
                if exec_index == 2:
                    info('''[CLI]Meet 'more', should send 'blank' to continue, Aerohive products''', self.is_info)
                if exec_index == 3:
                    info('''[CLI]Meet 'more', should send 'blank' to continue, Dell products''', self.is_info)
                if exec_index == 4:
                    info('''[CLI]Meet 'more', should send 'blank' to continue, H3C products''', self.is_info)                    
                # retry 9999 times, if not enough, we can add the value
                self._retry_not_expect_list(' ', 'send', [pexpect.TIMEOUT, expect, '--More--|More:|-- More --'], noexp_index_list=[0, 2], retrymode='repeat', retry=9999, interval=self.timeout)
                if self.exec_index == 1:
                    # send enter to remove the blank
                    self.child.sendline('')
                    self.child.expect([pexpect.TIMEOUT, self.prompt], self.timeout)
                else:
                    raise ValueError, '''Exec Error'''
            sleep(wait)
                
    def basic_logout(self):
        if self.mode == 'ssh':
            info('''[LOGOUT]SSH Logout Process''', self.is_info)
            self._retry_not_expect_list('d', 'sendcontrol', [pexpect.TIMEOUT, 'Connection to .* closed'], noexp_index_list=[0], retrymode='repeat')
            if self.exec_index == 0:
                raise ValueError, '''Logout timeout Error'''
            elif self.exec_index == 1:
                info('''[LOGOUT]SSH Logout successfully''', self.is_info)
        elif self.mode == 'telnet':
            info('''[LOGOUT]TELNET Logout Process''', self.is_info)
            self._retry_not_expect_list(']', 'sendcontrol', [pexpect.TIMEOUT, 'telnet>.*'], noexp_index_list=[0])
            if self.exec_index == 0:
                # send this cli again to confirm logout
                self._retry_not_expect_list(']', 'sendcontrol', [pexpect.TIMEOUT, 'telnet>.*'], noexp_index_list=[0])
                if self.exec_index == 0:
                    raise ValueError, '''Logout timeout Error'''
            elif self.exec_index == 1:
                self._retry_not_expect_list('q', 'sendline', [pexpect.TIMEOUT, 'Connection closed.*'], noexp_index_list=[0])
                if self.exec_index == 0:
                    raise ValueError, '''Logout timeout Error'''
                elif self.exec_index == 1:
                    info('''[LOGOUT]TELNET Logout successfully''', self.is_info)

    def _retry_not_expect(self, cli, mode, exp_list, noexp_index=0, retrymode='enter', retry=5, interval=5):
        if self.child:
            info('''[CLI]spawn child exist, send cli directly''', self.is_info)
            exec_cli = '''self.child.%s(cli)''' % mode
        else:
            info('''[CLI]spawn child not exist, create spawn firstly''', self.is_info)
            exec_cli = '''self.child=pexpect.spawn(cli)'''
        exec(exec_cli)
        self.exec_index = self.child.expect(list(exp_list), interval)
        if self.exec_index == noexp_index:
            info('''[RETRY]Trigger Retry Process''', self.is_info)
            info('''[RETRY]CLI         = %s''' % cli, self.is_info)
            info('''[RETRY]MODE        = %s''' % mode, self.is_info)
            info('''[RETRY]EXPECT_LIST = %s''' % str(exp_list), self.is_info)
            info('''[RETRY]RETRY_MODE  = %s''' % retrymode, self.is_info)
            info('''[RETRY]RETRY       = %s''' % retry, self.is_info)
            info('''[RETRY]INTERVAL    = %s''' % interval, self.is_info)
            for i in xrange(int(retry)):
                info('''[RETRY]Retry %s time start''' % (i + 1), self.is_info)
                if retrymode == 'enter':
                    self.child.sendline('')
                elif retrymode == 'repeat':
                    exec(exec_cli)
                self.exec_index = self.child.expect(list(exp_list), interval)
                if self.exec_index != noexp_index:
                    info('''[RETRY]Match expect, end Retry Process''', self.is_info)
                    return
                info('''[RETRY]Retry %s time end''' % (i + 1), self.is_info)
            info('''[RETRY]Retry %s times, still cannot get expect''' % retry, self.is_info)
        else:
            info('''[CLI]Match expect, no retry''', self.is_info)
            return
        raise ValueError, '''[RETRY]Retry %s times and still cannot match expect''' % retry

    def _retry_not_expect_list(self, cli, mode, exp_list, noexp_index_list=[0], retrymode='enter', retry=5, interval=5):
        if self.child:
            info('''[CLI]spawn child exist, send cli directly''', self.is_info)
            exec_cli = '''self.child.%s(cli)''' % mode
        else:
            info('''[CLI]spawn child not exist, create spawn firstly''', self.is_info)
            exec_cli = '''self.child=pexpect.spawn(cli)'''
        exec(exec_cli)
        self.exec_index = self.child.expect(list(exp_list), interval)
        if self.exec_index in noexp_index_list:
            info('''[RETRY]Trigger Retry Process''', self.is_info)
            info('''[RETRY]CLI         = %s''' % cli, self.is_info)
            info('''[RETRY]MODE        = %s''' % mode, self.is_info)
            info('''[RETRY]EXPECT_LIST = %s''' % str(exp_list), self.is_info)
            info('''[RETRY]RETRY_MODE  = %s''' % retrymode, self.is_info)
            info('''[RETRY]RETRY       = %s''' % retry, self.is_info)
            info('''[RETRY]INTERVAL    = %s''' % interval, self.is_info)
            for i in xrange(int(retry)):
                info('''[RETRY]Retry %s time start''' % (i + 1), self.is_info)
                if retrymode == 'enter':
                    self.child.sendline('')
                elif retrymode == 'repeat':
                    exec(exec_cli)
                self.exec_index = self.child.expect(list(exp_list), interval)
                if self.exec_index not in noexp_index_list:
                    info('''[RETRY]Match expect, end Retry Process''', self.is_info)
                    return
                info('''[RETRY]Retry %s time end''' % (i + 1), self.is_info)
            info('''[RETRY]Retry %s times, still cannot get expect''' % retry, self.is_info)
        else:
            info('''[CLI]Match expect, no retry''', self.is_info)
            return
        raise ValueError, '''[RETRY]Retry %s times and still cannot match expect''' % retry
     
    def _debug(self):
        self.is_debug = False
        self.is_info = False
        self.is_warn = False
        self.is_error = False
        if self.debug_level == 'debug':
            self.is_debug = True
            self.is_info = True
            self.is_warn = True
            self.is_error = True          
        elif self.debug_level == 'info':
            self.is_info = True
            self.is_warn = True
            self.is_error = True   
        elif self.debug_level == 'warn':
            self.is_warn = True
            self.is_error = True   
        elif self.debug_level == 'error':
            self.is_error = True
            
    def _tag(self):
        self.is_user = False
        self.is_passwd = False
        self.is_prompt = False
        self.is_no = False
        self.is_error = False

    def _cli(self):
        # the clis in config file will be added to the end of cli list
        self.exec_cli_list = self.cli_list
        if self.config_file:
            with open(self.config_file) as f_o:
                f_r_list = f_o.readlines()
            self.exec_cli_list.extend(f_r_list)
        self.c_m_e_t_w_list = generate_cli_mode_expect_timeout_wait_list(self.exec_cli_list, self.prompt, self.timeout, self.wait, self.passwd)

    def _port(self):
        # Due to the port can be used for either ssh or telnet, we should set its default value here
        # If you have set the value, it is no influnce here
        if self.port == -1:
            if self.mode == 'ssh':
                self.port = 22
            elif self.mode == 'telnet':
                self.port = 23

    def _logfile_init(self):
        self.f_o = None
        if self.log_file != 'stdout':
            #Modify mode from w to a for loop telnet control's file log
            self.f_o = open(self.log_file, mode='a')

    def _logfile_process(self):
        if self.f_o:
            self.f_o.close()
            with open(self.log_file, mode='r') as f_o:
                f_r = f_o.read()
            p1 = ' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08          \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08'
            p2 = ' {28}'
            p3 = '\r'
            p = '''%s|%s|%s''' % (p1, p2, p3)
            f_r = re.sub(p, '', f_r)
            with open(self.log_file, mode='w') as f_o:
                f_o.write(f_r) 

    def value(self, key):
        if self.para_dict.has_key(key):
            return self.para_dict[key]
