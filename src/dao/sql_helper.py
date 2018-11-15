# coding=utf8
# Copyright 2018 AGGRX Inc. All Rights Reserved.

"""
@author: ZengYaoPeng (zengyaopeng@tv365.net)
@time: 2018/10/10 下午7:45
"""
import MySQLdb


def build_insert_sql(table_name, column_kv_dict):
    # type: (str, dict) -> String
    column_name_list = []
    column_value_list = []
    column_kv_dict['create_time'] = column_kv_dict['update_time'] = ''
    for k in column_kv_dict:
        column_name_list.append(str("`%s`" % k))
        if k == 'create_time' or k == 'update_time':
            column_value_list.append("now()")
        else:
            column_value_list.append("'%s'" % (MySQLdb.escape_string(str(column_kv_dict[k]))))
    column_name_str = str("(%s)" % (','.join(column_name_list)))
    column_value_str = str("(%s)" % (','.join(column_value_list)))
    result = str('insert into %s %s values %s;' % (table_name, column_name_str, column_value_str))
    return result


def build_update_sql(table_name, column_kv_dict, condition_dict):
    # type: (str, dict, dict) -> String

    condition_list = []
    column_set_list = []
    column_kv_dict['update_time'] = ''
    for k in column_kv_dict:
        if k == 'update_time':
            column_set_list.append(str("`%s`=now()" % k))
        else:
            try:
                column_set_list.append(str("`%s`='%s'" % (k, MySQLdb.escape_string(str(column_kv_dict[k])))))
            except:
                pass
    column_set_str = str(" %s " % (','.join(column_set_list)))
    for k in condition_dict:
        condition_list.append(str("`%s`='%s'" % (k, str(condition_dict[k]))))
    condition_str = ' where ' + ' and '.join(condition_list)
    result = str('update %s set %s %s;' % (table_name, column_set_str, condition_str))
    return result


def build_where(condition_dict):
    # type: (dict) -> String
    condition_list = []
    for k in condition_dict:
        condition_list.append(str("`%s`='%s'" % (k, str(condition_dict[k]))))
    if len(condition_list) > 0:
        return ' where ' + ' and '.join(condition_list)
    else:
        return ''