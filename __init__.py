#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from bin import *

class VMware(object):
    def __init__(self):
        self.connect = ExpectConnect()
        if self.connect.mode=='ssh':
            self.connect.ssh_login()
        elif self.connect.mode=='telnet':
            self.connect.telnet_login()

    def __del__(self):
        self.connect._basic_logout()

        
    def add_vswitch_portgroup(self, portgroup_name, vswitch_name, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
# ##use esxcli, don't need to enter correct path
            add_vswitch_portgroup_command = '''esxcli network vswitch standard portgroup add --portgroup-name=%s --vswitch-name=%s''' % (portgroup_name, vswitch_name)
            print add_vswitch_portgroup_command
            ssh_login_result.sendline(add_vswitch_portgroup_command)
            ssh_login_result.expect('#')
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def del_vswitch_portgroup(self, portgroup_name, vswitch_name, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            del_vswitch_portgroup_command = '''esxcli network vswitch standard portgroup remove --portgroup-name=%s --vswitch-name=%s''' % (portgroup_name, vswitch_name)
            print del_vswitch_portgroup_command
            ssh_login_result.sendline(del_vswitch_portgroup_command)
            ssh_login_result.expect('#')
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def del_vswitch_all_portgroup(self, vswitch_name, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            get_vswitch_portgroup_command = 'esxcli network vswitch standard portgroup list'
            ssh_login_result.sendline(get_vswitch_portgroup_command)
            ssh_login_result.expect('#')
            vswitch_portgroup_file = ssh_login_result.before
# ##use /n instead of ^, ^ means begin of the file or variable, not lines
            vswitch_portgroup_list = re.findall(r'\n(\w+) +%s +\d+' % vswitch_name, vswitch_portgroup_file)
            print 'The portgroups of vswitch %s is as below' % vswitch_name
            print vswitch_portgroup_list
            for portgroup in vswitch_portgroup_list:
                del_vswitch_portgroup_command = 'esxcli network vswitch standard portgroup remove --portgroup-name=%s --vswitch-name=%s' % (portgroup, vswitch_name)
                ssh_login_result.sendline(del_vswitch_portgroup_command)
                index = ssh_login_result.expect(['#', '[0-9]+ active ports'])
                if index == 0:
                    print 'Delete port-group %s from %s successfully' % (portgroup, vswitch_name)
                elif index == 1:
                    print 'Delete port-group %s from %s failed, please remove the active ports firstly' % (portgroup, vswitch_name)
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None
        
    
    def bind_portgroup_vlan(self, portgroup_name, vlan, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            bind_vswitch_port_command = '''esxcli network vswitch standard portgroup set -p %s --vlan-id %s''' % (portgroup_name, vlan)
            print bind_vswitch_port_command
            ssh_login_result.sendline(bind_vswitch_port_command)
            ssh_login_result.expect('#')
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None
        

    def unbind_portgroup_vlan(self, portgroup_name, vlan, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            unbind_vswitch_port_command = '''esxcli network vswitch standard portgroup set --vlan-id %s -p %s''' % (vlan, portgroup_name)
            print unbind_vswitch_port_command
            ssh_login_result.sendline(unbind_vswitch_port_command)
            ssh_login_result.expect('#')
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def copy_vm_from_temple(self, datastore_path, src_folder, des_folder, ser_num, net_name, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            # ##enter operate path firstly
            ssh_login_result.sendline('cd %s' % datastore_path)
            ssh_login_result.expect('#')
            print 'Enter correct path'
            # ##copy file
            print 'Clear primary folder %s firstly' % des_folder
            copy_del_command = 'rm -r %s' % (des_folder)
            ssh_login_result.sendline(copy_del_command)
            ssh_login_result.expect('#')
            print 'Clear primary folder %s successfully, ready to copy' % des_folder
            copy_command = 'cp -fr %s %s' % (src_folder, des_folder)
            ssh_login_result.sendline(copy_command)        
            print 'Copying file, please wait'
            print '............'
            # ##v2 define copy time out
            ssh_login_result.expect('#', timeout=1200)
            print 'Folder %s has been copied successfully' % des_folder
            # Be careful of the path(remote/locate), python can open only locate file, not remote file, so cannot use open
            vmx_file_path = des_folder + '/' + src_folder + '.vmx'
            vmx_file_path_save = des_folder + '/' + src_folder + '.vmx.save'
            print 'Copying backup file'
            back_command = 'cp -f %s %s' % (vmx_file_path, vmx_file_path_save)
            ssh_login_result.sendline(back_command)
            ssh_login_result.expect('#')
            # ##modify serial(must begin more than 1024, this choose from 2001)
            # ##modify eth1 network
            # ##modify display name
            # ##bash script / need to be transfered to \/, and be careful of '' "" ''''''
            serial_port_sub = '''telnet:\/\/:%s''' % ser_num
            eth1_network_sub = '''ethernet1.networkName = "%s"''' % net_name
            display_name_sub = '''displayName = "%s"''' % des_folder
            sub_command = '''cat %s | sed \
            -e 's/telnet:..:[0-9]\{1,5\}/%s/' \
            -e 's/ethernet1.networkName = ".*"/%s/' \
            -e 's/displayName.*".*"/%s/' \
            > %s''' % (vmx_file_path_save, serial_port_sub, eth1_network_sub, display_name_sub, vmx_file_path)
            ssh_login_result.sendline(sub_command)
            ssh_login_result.expect('#')
            print 'Replace serial port successfully'
            print 'Replace eth1 network successfully'
            print 'Replace display name successfully' 
            # Add the attribute 'copy' to file to avoid show copy info
            ssh_login_result.sendline('cat %s' % vmx_file_path)
            # ##use '/vmfs.*#' may match the more than you want and cause answer.attribute miss
            ssh_login_result.expect('#')
            copy_attribute_file = ssh_login_result.before
            copy_attribute_exist = re.search(r'answer.msg.uuid.altered', copy_attribute_file)
            if copy_attribute_exist:
                # ##sub it
                print 'The answer attribute has been already configured, do nothing'
            else:
                # ##add it
                print 'No answer attribute, add it'
                add_command = '''echo 'answer.msg.uuid.altered = "I copied it"' >> %s''' % vmx_file_path
                ssh_login_result.sendline(add_command)
                ssh_login_result.expect('#')
                print 'Add attribute copy successfully'
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def del_vm(self, target_folder_path, spawn_child):
        # ##target_folder_path should be full path
        ssh_login_result = spawn_child
        if ssh_login_result:
            del_vm_command = 'rm -r %s' % target_folder_path
            ssh_login_result.sendline(del_vm_command)
            ssh_login_result.expect('#')            
            print 'Delete target_folder should be full path'
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None
        
    def reg_vm(self, vmx_path, spawn_child):
        # register the virtual machine as your display name
        ssh_login_result = spawn_child
        if ssh_login_result:
            reg_vm_command = 'vim-cmd solo/registervm %s' % (vmx_path)
            ssh_login_result.sendline(reg_vm_command)
            print reg_vm_command
            ssh_login_result.expect('#')
            print 'register successfully'
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def unreg_vm(self, vmx_path, spawn_child):
        # unregister the virtual
        ssh_login_result = spawn_child
        if ssh_login_result:
            unreg_vm_command = 'vim-cmd vmsvc/unregister %s' % (vmx_path)
            ssh_login_result.sendline(unreg_vm_command)
            print unreg_vm_command
            ssh_login_result.expect('#')
            print 'unregister successfully'
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None
    def rm_vm_folder(self, vm_folder_path, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            rm_vm_folder_command = 'rm -r %s' % (vm_folder_path)
            ssh_login_result.sendline(rm_vm_folder_command)
            print rm_vm_folder_command
            ssh_login_result.expect('#')
            print 'rm %s successfully' % vm_folder_path
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def power_on_all_vm(self, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            # ##Get the info of the vmid
            get_all_vmid_command = 'vim-cmd vmsvc/getallvms'
            ssh_login_result.sendline(get_all_vmid_command)
            ssh_login_result.expect('#')
            all_vmid_file = ssh_login_result.before
            # ##Be careful, this place cannot use '^\d+', because the ssh_login_result.before is not a file(/n can be shown in the variable)
            all_vmid_list = re.findall(r'\n(\d+)', all_vmid_file)
            print 'All vmids are in the below list'
            print all_vmid_list
            for vmid in all_vmid_list:
                ssh_login_result.sendline('vim-cmd vmsvc/power.on %s' % vmid)
                index = ssh_login_result.expect(['Power on failed', '#'])
                print 'Power up vmid %s successfully' % vmid
                if index == 0:
                    print 'Power on VM vmid %s failed, the VM may power on already' % vmid
                    # ##Be careful, match 'failed' may cause follow'\r\n~#' live to next cache, so need clear it
                    ssh_login_result.expect('#')
                elif index == 1: 
                    print 'Power on VM vmid %s successfully' % vmid
                return ssh_login_result
                print 'Power up vmid %s successfully' % vmid
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def power_off_all_vm(self, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            # ##Get the info of the vmid
            get_all_vmid_command = 'vim-cmd vmsvc/getallvms'
            ssh_login_result.sendline(get_all_vmid_command)
            ssh_login_result.expect('#')
            all_vmid_file = ssh_login_result.before
            # ##Be careful, this place cannot use '^\d+', because the ssh_login_result.before is not a file(/n can be shown in the variable)
            all_vmid_list = re.findall(r'\n(\d+)', all_vmid_file)
            print 'All vmids are in the below list'
            print all_vmid_list
            for vmid in all_vmid_list:
                ssh_login_result.sendline('vim-cmd vmsvc/power.off %s' % vmid)
                index = ssh_login_result.expect(['Power off failed', '#'])
                if index == 0:
                    print 'Power off VM vmid %s failed, the VM may power off already' % vmid
                    # ##Be careful, match 'failed' may cause follow'\r\n~#' live to next cache, so need clear it
                    ssh_login_result.expect('#')
                elif index == 1: 
                    print 'Power off VM vmid %s successfully' % vmid
                return ssh_login_result
                print 'Power off vmid %s successfully' % vmid
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def power_on_vm_via_vmname(self, vmname, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            # ##Get the vm_name correspond vmid
            get_all_vmid_command = '''vim-cmd vmsvc/getallvms | grep '%s ' ''' % vmname
            ssh_login_result.sendline(get_all_vmid_command)
            ssh_login_result.expect('#')
            vmid_file = ssh_login_result.before
            # ##Be careful, this place cannot use '^\d+', because the ssh_login_result.before is not a file(/n can be shown in the variable)
            vmid_list = re.findall(r'\n(\d+)', vmid_file)
            if len(vmid_list) == 1:
                print 'The %s vmid is %s' % (vmname, vmid_list[0])
                ssh_login_result.sendline('vim-cmd vmsvc/power.on %s' % vmid_list[0])
                index = ssh_login_result.expect(['Power on failed', '#'])
                print 'Power up vmid %s successfully' % vmid_list[0]
                if index == 0:
                    print 'Power on VM vmid %s failed, the VM may power on already' % vmid_list[0]
                    # ##Be careful, match 'failed' may cause follow'\r\n~#' live to next cache, so need clear it
                    ssh_login_result.expect('#')
                elif index == 1: 
                    print 'Power on VM vmid %s successfully' % vmid_list[0]
                return ssh_login_result
            else:
                print 'VM %s is not in this Blade server' % vmname
                ssh_login_result.close(force=True)
                return None
        else:
            print 'SSH login failure, please check input spawn child'
            return None

    def power_off_vm_via_vmname(self, vmname, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            # ##Get the vm_name correspond vmid
            get_all_vmid_command = '''vim-cmd vmsvc/getallvms | grep '%s ' ''' % vmname
            ssh_login_result.sendline(get_all_vmid_command)
            ssh_login_result.expect('#')
            vmid_file = ssh_login_result.before
            # ##Be careful, this place cannot use '^\d+', because the ssh_login_result.before is not a file(/n can be shown in the variable)
            vmid_list = re.findall(r'\n(\d+)', vmid_file)
            if len(vmid_list) == 1:
                print 'The %s vmid is %s' % (vmname, vmid_list[0])
                ssh_login_result.sendline('vim-cmd vmsvc/power.off %s' % vmid_list[0])
                index = ssh_login_result.expect(['Power off failed', '#'])
                if index == 0:
                    print 'Power off VM vmid %s failed, the VM may power off already' % vmid_list[0]
                    # ##Be careful, match 'failed' may cause follow'\r\n~#' live to next cache, so need clear it
                    ssh_login_result.expect('#')
                elif index == 1: 
                    print 'Power off VM vmid %s successfully' % vmid_list[0]
                return ssh_login_result
            else:
                print 'VM %s is not in this Blade server' % vmname
                ssh_login_result.close(force=True)
                return None
        else:
            print 'SSH login failure, please check input spawn child'
            return None
    def power_on_vm_via_vmid(self, vmid, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            ssh_login_result.sendline('vim-cmd vmsvc/power.on %s' % vmid)
            index = ssh_login_result.expect(['failed', '#', pexpect.EOF])
            if index == 0:
                print 'Power on VM vmid %s failed, the VM may power on already' % vmid
                # ##Be careful, match 'failed' may cause follow'\r\n~#' live to next cache, so need clear it
                ssh_login_result.expect('#')
            elif index == 1: 
                print 'Power on VM vmid %s successfully' % vmid
            elif index == 2:
                print 'power_on_vm_via_vmid meet EOF'
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None
        
    def power_off_vm_via_vmid(self, vmid, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            ssh_login_result.sendline('vim-cmd vmsvc/power.off %s' % vmid)
            index = ssh_login_result.expect(['failed', '#', pexpect.EOF])
            if index == 0:
                print 'Power off VM vmid %s failed, the VM may power off already' % vmid
                # ##Be careful, match 'failed' may cause follow'\r\n~#' live to next cache, so need clear it
                ssh_login_result.expect('#')
            elif index == 1: 
                print 'Power off VM vmid %s successfully' % vmid
            elif index == 2:
                print 'power_off_vm_via_vmid meet EOF'
            return ssh_login_result
        else:
            print 'SSH login failure, please check input spawn child'
            return None
        
    def vmname_to_vmid(self, vmname, spawn_child):
        ssh_login_result = spawn_child
        if ssh_login_result:
            # ##should add blank after %s such as "grep '%s ' ", because if we want to search xxx001, will shown all vmid(all file name is the same, such as 'VirtualOS_011/VirtualOS_001.vmx ')
            get_vmid_command = "vim-cmd vmsvc/getallvms | grep '%s '" % vmname
            print '''Get vmid command is "%s"''' % get_vmid_command
            ssh_login_result.sendline(get_vmid_command)
            index = ssh_login_result.expect(['#', pexpect.EOF])
            if index == 0:
                pass
            elif index == 1:
                print 'vmname_to_vmid meet EOF'
            vmid_file = ssh_login_result.before
            print 'VM %s correspond info is as below' % vmname
            print vmid_file
            vmid_list = re.findall(r'\n(\d+) ', vmid_file)
            if len(vmid_list) == 1:
                print 'Get %s correspond vmid %s successfully' % (vmname, vmid_list[0])
                return vmid_list[0]
            else:
                print 'Get %s correspond vmid failed,please check your vmname is in the blade server' % (vmname)
                ssh_login_result.close(force=True)
                return None
        else:
            print 'SSH login failure, please check input spawn child'
            return None
