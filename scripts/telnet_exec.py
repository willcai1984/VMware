  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware.unit import str2list
from VMware.expect import Expect

def telnet_exec():
    connect = Expect()
    ser_list = str2list(connect.value("vm.serial"))
    for ser in ser_list:
        connect.port = ser
        connect.telnet_login()
        connect.basic_exec()
        connect.basic_logout()
if __name__ == '__main__':
    telnet_exec()
