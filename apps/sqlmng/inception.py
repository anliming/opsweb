#coding=utf-8

import MySQLdb

def table_structure(dbaddr, dbname, sqlcontent):
    sql = '/* %s */\
      inception_magic_start;\
      use %s; %s inception_magic_commit;' % (dbaddr, dbname, sqlcontent)
    try:
        conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='',port=6669,db='',use_unicode=True,charset="utf8")  # 连接inception
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    return result

def getbak(sql, dbname=''):
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '123456', db = dbname, charset = 'utf8')
    conn.autocommit(True)
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

