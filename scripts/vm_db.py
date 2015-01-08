  #!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Author: Will

from VMware import VMware
from VMware.unit import str2list
import MySQLdb, time

def vm_db():
    vm = VMware()
    ip = vm.connect.ip
    sql_name = vm.connect.value("sql.name")
    sql_ip = vm.connect.value("sql.ip")
    sql_user = vm.connect.value("sql.user")
    sql_passwd = vm.connect.value("sql.passwd")
    con = MySQLdb.connect(host=sql_ip, user=sql_user, passwd=sql_passwd)
    cursor = con.cursor()
    cursor.execute("create database if not exists vmware")
    con.select_db('vmware')
    '''
    power:   0/1 off/on
    flag:    0/1 unactive/active
    '''
    create_table_cli="create table if not exists %s (vmid char(10) not null primary key,\
                      display varchar(200),register varchar(200),power char(1),flag char(1))" % sql_name
    cursor.execute(create_table_cli)
    db_sync(vm, con, cursor, sql_name)
    cursor.close()

def db_sync(vm, con, cursor, sql_name):
    vm._data()
    cursor.execute("update %s set flag='0'" % sql_name)
    for i in range(len(vm.id_list)):
        if vm.dis_list[i] in vm.poweron_list:
            cursor.execute("replace into %s(vmid,display,register,power,flag) values('%s','%s','%s','%s','%s')" % 
                                (sql_name,
                                vm.id_list[i],
                                vm.dis_list[i],
                                vm.reg_list[i],
                                '1', '1'))
        else:
            cursor.execute("replace into %s(vmid,display,register,power,flag) values('%s','%s','%s','%s','%s')" % 
                               (sql_name,
                                vm.id_list[i],
                                vm.dis_list[i],
                                vm.reg_list[i],
                                '0', '1'))
    con.commit()

if __name__ == '__main__':
    vm_db()
