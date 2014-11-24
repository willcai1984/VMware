  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
from VMware import VMware
from VMware.unit import str2list

def vm_vlandel():
    #Need power off the related vms firstly
    vm = VMware()
    vlan_list = str2list(vm.connect.value("vm.vlan"))
    vswitch = vm.connect.value("vm.vswitch")
    for vlan in vlan_list:
        vm.del_vswitch_portgroup(vswitch, vlan)
if __name__ == '__main__':
    vm_vlandel()
