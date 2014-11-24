  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list

def vm_del():
    vm = VMware()
    folder_path = vm.connect.value("vm.folder_path")
    name_list = str2list(vm.connect.value("vm.name_list"))
    is_all = vm.connect.value("vm.is_all")
    if is_all == "true":
        vm.power_off_vm_all()
        vm.unreg_vm_all(folder_path)
        vm.del_vm_all(folder_path)
    else:
        for name in name_list:
            vm.power_off_vm_via_vmname(name)
            vm.unreg_vm(folder_path, name + '/' + name + '.vmx')
            vm.del_vm(folder_path, name)

if __name__ == '__main__':
    vm_del()