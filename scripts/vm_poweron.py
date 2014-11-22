  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.bin.unit import str2list

def vm_poweron():
    vm = VMware()
    is_all = vm.connect.value("vm.is_all")
    name_list = str2list(vm.connect.value("vm.name_list"))
    if is_all=="true":
        vm.power_on_vm_all()
    else:
        for vmname in name_list:
            vm.power_on_vm_via_vmname(vmname)

if __name__ == '__main__':
    vm_poweron()
