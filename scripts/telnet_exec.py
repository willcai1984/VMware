  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list
from VMware.expect import Expect

def telnet_exec():
    vm = VMware()
    ser_list = str2list(vm.connect.value("vm.serial"))
    for ser in ser_list:
        vm = Expect()
        vm.port = ser
        vm.telnet_login()
        vm.basic_exec()
        vm.basic_logout()
if __name__ == '__main__':
    telnet_exec()
