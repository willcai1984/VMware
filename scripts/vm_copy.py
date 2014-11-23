  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list

def vm_copy():
    vm = VMware()
    folder_path = vm.connect.value("vm.folder_path")
    src = vm.connect.value("vm.src")
    dst_list = str2list(vm.connect.value("vm.dst"))
    is_poweron = vm.connect.value("vm.is_poweron")
    for dst in dst_list:
        vm.copy_vm(folder_path, src, dst)
        vm.reg_vm(folder_path , dst + '/' + dst + '.vmx')
        if is_poweron == "true":
            vm.power_on_vm_via_vmname(dst)
if __name__ == '__main__':
    vm_copy()
