#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list

def vm_sub():
    vm = VMware()
    folder_path = vm.connect.value("vm.folder_path")
    name_list = str2list(vm.connect.value("vm.name"))
    is_serial = vm.connect.value("vm.is_serial")
    ser_list = str2list(vm.connect.value("vm.serial"))
    is_eth0 = vm.connect.value("vm.is_eth0")
    eth0_list = str2list(vm.connect.value("vm.eth0"))
    is_eth1 = vm.connect.value("vm.is_eth1")
    eth1_list = str2list(vm.connect.value("vm.eth1"))
    if len(name_list) != len(ser_list):
        raise ValueError, '''The length of vm.name "%s" and vm.serial "%s" is not the same''' % (str(name_list), str(ser_list))
    for name in name_list:
        vmx = (folder_path + '/' + name + '/' + name + '.vmx').replace('//', '/')
        if is_serial != "false": 
            ser = ser_list[name_list.index(name)]
            vm.sub_vm(vmx, sernum=ser)
        if is_eth0 != "false":
            if is_eth0 == "fix":
                eth0_list = [eth0_list[0]] * len(name_list)
            eth0 = eth0_list[name_list.index(name)]
            vm.sub_vm(vmx, eth0net=eth0)
        if is_eth1 != "false":
            if is_eth1 == "fix":
                eth1_list = [eth1_list[0]] * len(name_list)
            eth1 = eth1_list[name_list.index(name)]
            vm.sub_vm(vmx, eth1net=eth1)

if __name__ == '__main__':
    vm_sub()
