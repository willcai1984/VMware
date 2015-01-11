  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list

def vm_poweron():
    vm = VMware()
    is_all = vm.connect.value("vm.is_all")
    is_id = vm.connect.value("vm.is_id")
    name_list = str2list(vm.connect.value("vm.name"))
    id_list = str2list(vm.connect.value("vm.id"))
    if is_all == "true":
        vm.power_on_vm_all()
    else:
        if is_id == "false":
            for vmname in name_list:
                vm.power_on_vm_via_vmname(vmname)
        elif is_id == "true":
            for vmid in id_list:
                vm.power_on_vm_via_vmid(vmid)
if __name__ == '__main__':
    vm_poweron()
