  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will
try:
    import pexpect, re, os
except ImportError, e:
    raise ImportError (str(e) + """A critical module was not found. Probably this operating system does not support it.""")
from expect import Expect
from unit import sleep, debug, info, warn, error

class VMware(object):
    def __init__(self):
        self.connect = Expect()
        self.connect.ssh_login()

    def __del__(self):
        self.connect.basic_logout()

    def add_vswitch_portgroup(self, vswitch, portgroup):
        # use esxcli, don't need to enter correct path
        cli = '''esxcli network vswitch standard portgroup add --portgroup-name=%s --vswitch-name=%s''' % (portgroup, vswitch)
        self._exec(cli, head='ADD_PG')
        
    def del_vswitch_portgroup(self, vswitch, portgroup):
        cli = '''esxcli network vswitch standard portgroup remove --portgroup-name=%s --vswitch-name=%s''' % (portgroup, vswitch)
        self._exec(cli, head='DEL_PG')

    def del_vswitch_all_portgroup(self, vswitch):
        cli = 'esxcli network vswitch standard portgroup list'
        self._exec(cli, head='DEL_ALLPG')
        v_p = self.connect.child.before
        # use /n instead of ^, ^ means begin of the file or variable, not lines
        v_p_list = re.findall(r'\n(\w+) +%s +\d+' % vswitch, v_p)
        for p in v_p_list:
            self.del_vswitch_portgroup(vswitch, p)
    
    def bind_portgroup_vlan(self, portgroup_name, vlan):
        cli = '''esxcli network vswitch standard portgroup set -p %s --vlan-id %s''' % (portgroup_name, vlan)
        self._exec(cli, head='BIND_VLAN')

    def unbind_portgroup_vlan(self, portgroup_name, vlan):
        cli = '''esxcli network vswitch standard portgroup set --vlan-id %s -p %s''' % (vlan, portgroup_name)
        self._exec(cli, head='UNBIND_VLAN')

    def copy_vm(self, folder_path, src, dst):
        cli = 'cd %s' % folder_path
        self._exec(cli, head='COPY_VM')
        cli = 'rm -fr %s' % dst
        self._exec(cli, head='COPY_VM')
        cli = 'cp -fr %s %s' % (src, dst)
        self._exec(cli, timeout=1200, head='COPY_VM')
        vmx_s= dst + '/' + src + '.vmx'
        vmx_d = dst + '/' + dst + '.vmx'
        cli = 'cp -f %s %s' % (vmx_s, vmx_d)
        self._exec(cli, head='COPY_VM')
        #sub display name
        #Cannot use cat v | ... >v, we should use cat v.bak | .. > v instead, else , we can get a null v, include nothing 
        display_name_sub = '''displayName = "%s"''' % dst
        cli = '''cat %s | sed \
                 -e 's/displayName.*".*"/%s/' \
                 > %s''' % (vmx_s, display_name_sub, vmx_d)
        self._exec(cli, head='COPY_VM')
        cli = 'cat %s' % vmx_d
        self._exec(cli, head='COPY_VM')
        copy_attribute = self.connect.child.before
        is_c_a = re.search(r'answer.msg.uuid.altered', copy_attribute)
        if is_c_a:
            info('''[COPY_VM]The answer attribute has been already configured, do nothing''', self.connect.is_info)
        else:
            # add it
            info('''[COPY_VM]No answer attribute, add it''', self.connect.is_info)
            cli = '''echo 'answer.msg.uuid.altered = "I copied it"' >> %s''' % vmx_d
            self._exec(cli, head='COPY_VM')

    def sub_vm(self, vmx, ser_num, net_name):
        vmx_s=vmx
        vmx_b=vmx+'.bak'
        cli = 'cp -f %s %s' % (vmx_s, vmx_b)
        self._exec(cli, head='COPY_VM')
        serial_port_sub = '''telnet:\/\/:%s''' % ser_num
        eth1_network_sub = '''ethernet1.networkName = "%s"''' % net_name
        cli = '''cat %s | sed \
                 -e 's/telnet:..:[0-9]\{1,5\}/%s/' \
                 -e 's/ethernet1.networkName = ".*"/%s/' \
                 > %s''' % (vmx_b, serial_port_sub, eth1_network_sub, vmx_s)
        self._exec(cli, head='SUB_VM')

    def del_vm(self, folder_path, folder_name):
        cli = 'rm -fr %s' % (folder_path + '/' + folder_name)
        self._exec(cli, head='DEL_VM')
    
    def del_vm_all(self, folder_path):
        cli = 'cd %s;rm -fr *' % (folder_path)
        self._exec(cli, head='DEL_VM')
    
    def reg_vm(self, folder_path, reg_name):
        # register the virtual machine as your display name
        cli = 'vim-cmd solo/registervm %s' % (folder_path + '/' + reg_name)
        self._exec(cli, head='REG_VM')

    def unreg_vm(self, folder_path, reg_name):
        # unregister the virtual
        cli = 'vim-cmd vmsvc/unregister %s' % (folder_path + '/' + reg_name)
        self._exec(cli, head='UNREG_VM')

    def unreg_vm_all(self, folder_path):
        reg_name_list = self._get_all_reg()
        for reg_name in reg_name_list:
            self.unreg_vm(folder_path, reg_name)

    def _is_vmid_exist(self, vmid):
        cli = 'vim-cmd vmsvc/getallvms'
        self._exec(cli, head='CHECK_VMID')
        vmid_all = self.connect.child.before
        vmid_list = re.findall(r'\n(\d+)', vmid_all)
        if vmid in vmid_list:
            return True
        else:
            return False

    def _get_all_vmid(self):
        cli = 'vim-cmd vmsvc/getallvms'
        self._exec(cli, head='ALL_VMID')
        vmid_all = self.connect.child.before
        vmid_list = re.findall(r'\n(\d+)', vmid_all)
        return vmid_list

    def _get_all_reg(self):
        cli = 'vim-cmd vmsvc/getallvms'
        self._exec(cli, head='ALL_REG')
        reg_all = self.connect.child.before
        reg_list = re.findall(r'\n\d+\s+\S+\s+\S+\s+(\S+)\s+', reg_all)
        return reg_list

    def power_on_vm_via_vmid(self, vmid):
        if self._is_vmid_exist:
            cli = 'vim-cmd vmsvc/power.on %s' % vmid
            self._exec(cli, head='POWER_ON')
        else:
            info('''[POWER_ON]Not find the vmid %s in vmid_list, skip''' % vmid, self.connect.is_info)
        
    def power_off_vm_via_vmid(self, vmid):
        if self._is_vmid_exist:
            cli = 'vim-cmd vmsvc/power.off %s' % vmid
            self._exec(cli, head='POWER_OFF')
        else:
            info('''[POWER_OFF]Not find the vmid %s in vmid_list, skip''' % vmid, self.connect.is_info)

    def vmname2vmid(self, vmname):
        # should add blank after %s such as "grep '%s ' ", because if we want to search xxx001, will shown all vmid(all file name is the same, such as 'VirtualOS_011/VirtualOS_001.vmx ')
        cli = "vim-cmd vmsvc/getallvms | grep '%s '" % vmname
        self._exec(cli, head='NAME2ID')
        vmid_all = self.connect.child.before
        vmid_list = re.findall(r'\n(\d+) ', vmid_all)
        if len(vmid_list) == 1:
            return vmid_list[0]
        else:
            info('''[NAME2ID]Not find the vmname %s in vmname_list, skip''' % vmname, self.connect.is_info)
            return None

    def power_on_vm_via_vmname(self, vmname):
        vmid = self.vmname2vmid(vmname)
        if vmid:
            self.power_on_vm_via_vmid(vmid)

    def power_off_vm_via_vmname(self, vmname):
        vmid = self.vmname2vmid(vmname)
        if vmid:
            self.power_off_vm_via_vmid(vmid)

    def power_on_vm_all(self):
        vmid_list = self._get_all_vmid()
        sort_vmid_list = [int(i) for i in vmid_list].sort()
        for vmid in sort_vmid_list:
            self.power_on_vm_via_vmid(vmid)

    def power_off_vm_all(self):
        vmid_list = self._get_all_vmid()
        sort_vmid_list = [int(i) for i in vmid_list].sort()
        for vmid in sort_vmid_list:
            self.power_off_vm_via_vmid(vmid)

    def _exec(self, cli, timeout=60, head=''):
        self.connect.child.sendline(cli)
        exp_list = [pexpect.TIMEOUT, pexpect.EOF, '[Ff]ail', self.connect.prompt]
        self.index = self.connect.child.expect(exp_list, timeout)
        if self.index == 0:
            info('''[%s]Meet Timeout''' % head, self.connect.is_info)
            info('''[%s]BEFORE = %s''' % (head, self.connect.child.before) , self.connect.is_info)
            info('''[%s]AFTER  = %s''' % (head, self.connect.child.after) , self.connect.is_info)
        elif self.index == 1: 
            info('''[%s]Meet EOF''', self.connect.is_info)
            info('''[%s]BEFORE = %s''' % (head, self.connect.child.before) , self.connect.is_info)
            info('''[%s]AFTER  = %s''' % (head, self.connect.child.after) , self.connect.is_info)
        elif self.index == 2:
            info('''[%s]Meet Failed''', self.connect.is_info)
            info('''[%s]BEFORE = %s''' % (head, self.connect.child.before) , self.connect.is_info)
            info('''[%s]AFTER  = %s''' % (head, self.connect.child.after) , self.connect.is_info)
        elif self.index == 3:
            info('''[%s]Execute CLI "%s"''' % (head, cli), self.connect.is_info)
        else:
            info('''[%s]Meet Failed''' % head, self.connect.is_info)
            info('''[%s]BEFORE = %s''' % (head, self.connect.child.before) , self.connect.is_info)
            info('''[%s]AFTER  = %s''' % (head, self.connect.child.after) , self.connect.is_info)
