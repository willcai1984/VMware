  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

try:
    import re, time, sys, os, json
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")

'''
Get the default data file name
'''
def get_default_data_file():
    test = sys.argv[0]
    test_dir, test_file = os.path.split(test)
    return os.path.join(test_dir, '%s.json' % os.path.splitext(test_file)[0])

'''
Get data from json file
'''
def josn_process(j_f):
    with open(j_f) as f_o:
        f_r = f_o.read()
    f_j = json.loads(f_r)
    j_dict = {}
    if f_j:
        for key1 in f_j:
            if type(f_j[key1]) == type({}):
                for key2 in f_j[key1]:
                    if type(f_j[key1][key2]) == type({}):
                        raise AssertionError, '''Cannot support 3rd json "%s" now''' % f_j[key1][key2]
                    elif type(f_j[key1][key2]) == type('') or type(f_j[key1][key2]) == type(u''):
                        j_dict['%s.%s' % (key1, key2)] = f_j[key1][key2]
                    else:
                        raise AssertionError, '''Key "%s" and Value "%s" is not as expect''' % (key2, f_j[key1][key2])
            elif  type(f_j[key1]) == type('') or  type(f_j[key1]) == type(u''):
                j_dict[key1] = f_j[key1]
            else:
                raise AssertionError, '''Key "%s" and Value "%s" is not as expect''' % (key1, f_j[key1])
    return j_dict


'''
Sleep
'''
def sleep(mytime=1):
    time.sleep(mytime)

'''
Print log based on debug level
'''
def debug(msg, is_debug):
    if msg and is_debug:
            print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def info(msg, is_info):
    if msg and is_info:
            print '%s INFO ' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def warn(msg, is_warn):
    if msg and is_warn:
            print '%s WARN ' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg
            
def error(msg, is_error):
    if msg and is_error:
            print '%s ERROR' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            print msg

'''
Transfer str to list
for example: 
>>> str2list('1,3,5-8,10')
['1', '3', '5', '6', '7', '8', '10']

>>> str2list('vm001,vm003-vm005,vm007')
['vm001', 'vm003', 'vm004', 'vm005', 'vm007']
'''
def str2list(list_str):
    p_list = list_str.split(',')
    para_reg = re.compile('^\w+')
    ran_reg = re.compile('^\w+-\w+$')
    str_reg = re.compile('\D*')
    int_reg = re.compile('\d+')
    # remove not int para and blank
    i_list = [i.replace(' ', '') for i in p_list if para_reg.search(i)]
    str_list = []
    for i in i_list:
        if ran_reg.search(i):
            ran_list = i.split('-')
            ran_start = ran_list[0]
            str_start = str_reg.search(ran_start).group()
            int_start = int_reg.search(ran_start).group()
            ran_end = ran_list[-1]
            str_end = str_reg.search(ran_end).group()
            int_end = int_reg.search(ran_end).group()
            for j in range(int(int_start), int(int_end) + 1):
                para = str(j)
                if str_start and str_start == str_end:
                    int_len = len(int_start)
                    int_j = ''
                    int_cli = '''int_j="%0''' + str(int_len) + '''d" % j'''
                    exec(int_cli)
                    para = str_start + str(int_j)
                str_list.append(para)
        else:
            str_list.append(str(i))
    return str_list


'''
Special cli process
'''
def generate_cli_mode_expect_timeout_wait_list(cli_list, prompt, timeout, wait, passwd='', sp=''):
    # define private parameters
    cli_mode_expect_timeout_wait_list = [] 
    reboot_timeout = 300
    save_img_timeout = 1200
    mode = 'sendline'
    # def special clis
    log_regex = re.compile('^show log.*')
    reset_config_regex = re.compile('^reset config$')
    reset_boot_regex = re.compile('^reset config bootstrap$') 
    reboot_regex = re.compile('^reboot$|^reboot backup$|^reboot current$|reboot offset')
    save_config_regex = re.compile('^save config tftp:.* (current|bootstrap)')
    save_image_regex = re.compile('^save image tftp:.*img')
    save_image_reboot_regex = re.compile('^save image tftp:.*now$')
    shell_regex = re.compile('^_shell$')
    exit_regex = re.compile('^exit$')
    enble_regex = re.compile('^enable$')
    country_regex = re.compile('^boot-param country-code.*')
    ctrl_regex = re.compile('ctrl-.*')
    reset_regex = re.compile('^reset$')
    quit_regex = re.compile('^quit$')
    scp_vpn_regex = re.compile('^save vpn.*scp.*')
    scp_img_regex = re.compile('^save image scp.*')
    scp_toconfig_regex = re.compile('^save config (current|bootstrap) scp.*')
    scp_fromconfig_regex = re.compile('^save config scp.* (current|bootstrap)')
    scp_transfer_regex = re.compile(r'> *scp:')
    # process special clis
    for cli in cli_list:        
        if log_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, '\w+.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('', mode, prompt, timeout, wait))
        elif reset_boot_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'bootstrap configuration.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, reboot_timeout, wait))
        elif reset_config_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'bootstrap configuration.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('', mode, 'login:', reboot_timeout, wait))
        elif reboot_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'Do you really want to reboot.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('', mode, 'login:.*', reboot_timeout, wait))             
        elif save_config_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'configuration.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, timeout, wait))
        elif save_image_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, r'update image.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, save_img_timeout, wait))
        elif save_image_reboot_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'update image.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, save_img_timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('', mode, 'login:.*', reboot_timeout, wait))
        elif shell_regex.search(cli):
            if sp:
                cli_mode_expect_timeout_wait_list.append((cli, mode, '[Pp]assword|%s' % prompt, timeout, wait))
                cli_mode_expect_timeout_wait_list.append((sp, mode, prompt, timeout, wait))
            else:
                cli_mode_expect_timeout_wait_list.append((cli, mode, prompt, timeout, wait))
        elif exit_regex.search(cli):
            if sp:
                cli_mode_expect_timeout_wait_list.append((cli, mode, prompt, timeout, wait))                
            else:
                cli_mode_expect_timeout_wait_list.append(('save config', mode, prompt, timeout, wait))
                cli_mode_expect_timeout_wait_list.append((cli, mode, 'login:.*|%s' % prompt, timeout, wait))  
        elif enble_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, '[Pp]assword.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append((passwd, mode, prompt, timeout, wait))             
        elif country_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'To apply radio setting.*it now\?.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, prompt, timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('', mode, 'login:.*', reboot_timeout, wait))  
        elif ctrl_regex.search(cli):
            cli = re.sub('[Cc]trl-', '', cli)
            if  re.search('\+', cli):
                cli_list = cli.split('+')
                real_index = 0
                for real_cli in cli_list:
                    if real_index == 0:
                        cli_mode_expect_timeout_wait_list.append((real_cli, 'sendcontrol', 'None', timeout, wait))
                    elif real_index == len(cli_list) - 1:
                        cli_mode_expect_timeout_wait_list.append((real_cli, 'send', prompt, timeout, wait))
                    else:
                        cli_mode_expect_timeout_wait_list.append((real_cli, 'send', 'None', timeout, wait))
                    real_index += 1
            else:
                cli_mode_expect_timeout_wait_list.append((cli, 'sendcontrol', prompt, timeout, wait))
        elif reset_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'login:.*', reboot_timeout, wait))
        elif quit_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, '%s|login:.*' % prompt, timeout, wait))
        elif scp_vpn_regex.search(cli) or scp_img_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, '[Pp]assword:.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append((passwd, mode, prompt, timeout, wait))
        elif scp_toconfig_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, '[Pp]assword:.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append((passwd, mode, prompt, timeout, wait))      
        elif scp_fromconfig_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, 'config to .* configuration.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append(('y', mode, '[Pp]assword:.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append((passwd, mode, prompt, timeout, wait))         
        elif scp_transfer_regex.search(cli):
            cli_mode_expect_timeout_wait_list.append((cli, mode, '[Pp]assword:.*', timeout, wait))
            cli_mode_expect_timeout_wait_list.append((passwd, mode, prompt, timeout, wait))
        else:
            cli_mode_expect_timeout_wait_list.append((cli, mode, prompt, timeout, wait))
    return cli_mode_expect_timeout_wait_list

