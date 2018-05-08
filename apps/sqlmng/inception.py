#coding=utf-8

import MySQLdb

def table_structure(dbaddr, dbname, sqlcontent):
    sql = '/* %s */\
      inception_magic_start;\
      use %s; %s inception_magic_commit;' % (dbaddr, dbname, sqlcontent)
    try:
<<<<<<< HEAD
<<<<<<< HEAD
        #conn = MySQLdb.connect(host='172.16.98.12',user='root',passwd='',db='',port=6669,use_unicode=True, charset="utf8")
=======
>>>>>>> 5183de7293c78238524527d0a26fb25f8c2faf14
=======
>>>>>>> 5183de7293c78238524527d0a26fb25f8c2faf14
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
<<<<<<< HEAD
<<<<<<< HEAD
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = 'xinwei', db = dbname, charset = 'utf8')
=======
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '123456', db = dbname, charset = 'utf8')
>>>>>>> 5183de7293c78238524527d0a26fb25f8c2faf14
=======
    conn = MySQLdb.connect(host = '127.0.0.1', port = 3306, user = 'root', passwd = '123456', db = dbname, charset = 'utf8')
>>>>>>> 5183de7293c78238524527d0a26fb25f8c2faf14
    conn.autocommit(True)
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

