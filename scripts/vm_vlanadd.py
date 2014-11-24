  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
import re
from VMware import VMware
from VMware.unit import str2list


def vm_vlanadd():
    vm = VMware()
    vlan_list = str2list(vm.connect.value("vm.vlan"))
    vswitch = vm.connect.value("vm.vswitch")
    int_reg = re.compile('\d+')
    for vlan in vlan_list:
        vm.add_vswitch_portgroup(vswitch, vlan)
        vlan_id = int(int_reg.search(vlan).group())
        vm.bind_portgroup_vlan(vlan, vlan_id)
        
if __name__ == '__main__':
    vm_vlanadd()
