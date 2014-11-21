#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware

def vm_copy():
    vm= VMware()
    folder_path=vm.connect.value("vm.folder_path")
    src=vm.connect.value("vm.src")
    des_list=vm.connect.value("vm.des_list").split(',')
    for des in des_list:
        vm.copy_vm(folder_path, src, des)

if __name__=='__main__':
    vm_copy()