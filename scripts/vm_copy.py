  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.bin.unit import str2list

def vm_copy():
    vm = VMware()
    folder_path = vm.connect.value("vm.folder_path")
    src = vm.connect.value("vm.src")
    des_list = str2list(vm.connect.value("vm.des"))
    is_poweron = vm.connect.value("vm.is_poweron")
    for des in des_list:
        vm.copy_vm(folder_path, src, des)
        vm.reg_vm(folder_path , des + '/' + des + '.vmx')
        if is_poweron == "true":
            vm.power_on_vm_via_vmname(des)
if __name__ == '__main__':
    vm_copy()
