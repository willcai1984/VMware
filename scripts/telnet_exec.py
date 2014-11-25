  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
import os
from VMware.unit import str2list
from VMware.expect import Expect

def telnet_exec():
    connect = Expect()
    ser_list = str2list(connect.value("vm.serial"))
    user = connect.value("vm.user")
    passwd = connect.value("vm.passwd")
    prompt = connect.value("vm.prompt")
    os.system('''echo ''>%s''' % connect.log_file)
    for ser in ser_list:
        connect = Expect()
        connect.port = ser
        connect.user = user
        connect.passwd = passwd
        connect.prompt = prompt
        connect.telnet_login()
        connect.basic_exec()
        connect.basic_logout()
if __name__ == '__main__':
    telnet_exec()
