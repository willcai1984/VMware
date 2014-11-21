#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware

def vm_poweron():
    vm= VMware()
    is_all=vm.connect.value("vm.is_all")
    name_list=vm.connect.value("vm.name_list").split(',')
    if is_all:
        vm.power_on_vm_all()
    else:
        for vmname in name_list:
            vm.power_on_vm_via_vmname(vmname)

if __name__=='__main__':
    vm_poweron()