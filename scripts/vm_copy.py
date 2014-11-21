#!/usr/bin/env python
# Filename: copy_vm.py
# Function: Copy VMs from temple VM, Register and Power on
###VM name begin with loop-begin your set, VirtualOS_xxx; serial_port is 2xxx; group-port is vSwitchx_1xxx, and the vlan is 1xxx
###If you want to copy VirtualOS_050 to VirtualOS_055
###Use command '''python vm_copy.py -d '10.155.32.134' -lb 50 -l 5  '''
# coding:utf-8
# Author: Well
from vm import *
import pexpect,re,argparse
def copy_register_poweron_vm(host,user,password,temple_vm_name,vswitch_name,copy_range):
###Define copy_login to class vm
    copy_login=vm(host,user,password)
    for i in copy_range:
        ###Generate portgroup name first
        portgroup_name = '%s_1%03d' % (vswitch_name,i)
        copy_add_group=copy_login.add_vswitch_portgroup(portgroup_name,vswitch_name,copy_login.spawn_child)
        ###Bind vlan to portgroup
        vlan = '1%03d' % i
        copy_bind_vlan=copy_login.bind_portgroup_vlan(portgroup_name,vlan,copy_add_group)
        ###Copy VM from temple
        src_folder=temple_vm_name
        des_folder=re.sub(r'\d+','%03d' % i,src_folder)
        ser_num='2%03d' % i
        net_name=portgroup_name
        copy_vm_result=copy_login.copy_vm_from_temple('/vmfs/volumes/datastore1',src_folder,des_folder,ser_num,net_name,copy_bind_vlan)
        print 'Copy %s successfully' % des_folder
        ###Register the VM
        vmx_path='/vmfs/volumes/datastore1/%s/%s.vmx' % (des_folder,src_folder)
        copy_vm_reg=copy_login.reg_vm(vmx_path,copy_vm_result)
        print 'Register %s successfully' % des_folder
        ###Power on the VM
#        vmname=des_folder
#        copy_poweron_vm=copy_login.power_on_vm_via_vmname(vmname,copy_vm_reg)
#        print 'Power on %s successfully'% des_folder
    return copy_vm_reg

###set parse to Class 'argparse.ArgumentParser'
parse = argparse.ArgumentParser(description='Copy VMs from temple VM, Register and Power on')

###Cannot use -h, conflict with the help argument
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='root', dest='loginname',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='loginpassword',
                    help='Login Password')

parse.add_argument('-s', '--switchname', required=False, default='vSwitch3', dest='vswitchname',
                    help='vSwitch Name, be careful of the format of the vSwitch name')

parse.add_argument('-t', '--templename', required=False, default='VirtualOS_001', dest='templetname',
                    help='Temple folder name')

parse.add_argument('-l', '--loopnum', required=False, default=1, type=int,  dest='loop',
                    help='Loop times')                    

parse.add_argument('-lb', '--loopbegin', required=False, default=2, type=int, dest='loopbegin',
                    help='loop begin number, default =')

def main():
    args = parse.parse_args()
    host = args.desip
    user = args.loginname
    password = args.loginpassword
    temple_vm_name = args.templetname
    vswitch_name = args.vswitchname
    copy_begin = args.loopbegin
    copy_num = args.loop
    copy_range = []
    for i in range(copy_num):
        copy_range_member=copy_begin+i
        copy_range.append(copy_range_member)
    ###need judge if all the members are correctly
    for i in copy_range:
        if i > 1 and i <= 999:
            pass
        else:
            print 'The script can only process loop num between 2 and 999, please check you input'
            return None
    copy_vmname_range=[]
    ###if modify temple name may cause error
    if temple_vm_name == 'VirtualOS_001':
        for i in range(len(copy_range)):
            copy_vmname_range.append('VirtualOS_%03d' % copy_range[i])
        print 'Copy destination folder list is as below'
        print copy_vmname_range
    copy_result=copy_register_poweron_vm(host,user,password,temple_vm_name,vswitch_name,copy_range)
    return copy_result

if __name__=='__main__':
    try:
        copy_register_poweron_result=main()
    except Exception, e:
        print str(e)
    else:
        if copy_register_poweron_result:
            copy_register_poweron_result.close()
            print 'Copy all VMs from temple VM, Register and Power on successfully'
        else:
            print 'Copy all VMs from temple VM, Register and Power on failed'
    