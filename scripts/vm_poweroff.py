#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list

def vm_poweroff():
    vm= VMware()
    is_all=vm.connect.value("vm.is_all")
    name_list = str2list(vm.connect.value("vm.name"))
    if is_all=="true":
        vm.power_off_vm_all()
    else:
        for vmname in name_list:
            vm.power_off_vm_via_vmname(vmname)

if __name__=='__main__':
    vm_poweroff()