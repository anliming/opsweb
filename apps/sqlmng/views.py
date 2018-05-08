#coding=utf-8
from django.forms.models import model_to_dict
from django.views.generic import View, TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import QueryDict,JsonResponse
from .models import *
from django.shortcuts import render
from basemodel.tasks import send_mail
from basemodel.dbcrypt import prpcrypt
from basemodel.page import JuncheePaginator
from dashboard.models import UserProfile
import re, commands, ConfigParser
import inception

# Create your views here.
conffile = "sqlmng/targets.conf"
crykey = 'aaa0aaa0aaa0aaa0'

def iptconf(conffield):  # 读配置文件
    cf = ConfigParser.ConfigParser()
    cf.read(conffile)
    inception_conf = cf.items(conffield)
    return inception_conf

class inception_result(LoginRequiredMixin, View):
    list_page = 'sqlmng/inception_result.html'  # 前端模板名
    detail_page = 'sqlmng/inception_sqldetail.html'
    usermodel = UserProfile
    inceptionmodel = InceptSql  # 数据模型名
    pk_url_kwarg = 'pk'

    def get_queryset(self):  # 数据库查询的结果，对应于context_object_name
        userobj = self.request.user
        if userobj.is_superuser:  # 管理员
            sqlret = self.inceptionmodel.objects.all()
            return sqlret
        role = userobj.userprofile.role
        if role == '1':  # 总监
            sqlret = self.inceptionmodel.objects.filter(commiter=userobj.username)
            g = userobj.groups.first()  # 组
            for u in g.user_set.values():  # 遍历组内所有的用户
                usqls = self.inceptionmodel.objects.filter(commiter=u['username'], env=1)
                sqlret = sqlret | usqls
        else:  # 研发或经理
            sqlret = userobj.inceptsql_set.all()
        return sqlret

    def get(self, request, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:  # 请求单用户数据
            sqlobj = InceptSql.objects.get(pk=pk)
            role = request.user.userprofile.role
            ret = {'sql': sqlobj, 'role': role}
            return render(request, self.detail_page, ret)
        else:  # 请求所有用户数据（复制的 BaseListView 的get方法）
            qs = self.get_queryset()
            page_num = request.GET.get('page', 1)  # 请求的第几页
            pageobj = JuncheePaginator(qs)
            wdata = pageobj.pagecomputer(page_num)
            return render(request, self.list_page, {'res_data': wdata[0], 'allpages': wdata[1], 'role': request.user.userprofile.role})

    # 执行/回滚/放弃...
    def post(self, request, **kwargs):
        #webdata = QueryDict(request.body).dict()
        sqlid = kwargs.get('pk')
        actiontype = kwargs.get('actiontype')
        sqlinfo = InceptSql.objects.get(id=sqlid)
        username = request.user.get_username()
        dbname = sqlinfo.dbname  # 取数据库名
        ret = {'status':0}
        if actiontype == 'execute':
            sqlcontent = sqlinfo.sqlcontent
            env = sqlinfo.env
            # 根据选择的数据库环境，匹配地址
            dbobj = dbconf.objects.filter(name=dbname, env=env)[0]
            pc = prpcrypt(crykey)
            dbpasspwd = pc.decrypt(dbobj.password)
            dbaddr = '--user=%s; --password=%s; --host=%s; --port=%s; --enable-execute;' % (dbobj.user, dbpasspwd, dbobj.host, dbobj.port)
            # 配置文件的inception部分
            # 执行SQL（防止同一个SQL被人已执行了，这边还没刷新 但点了执行，产生bug。执行前先检查status）
            sqlstatus = sqlinfo.status
            if sqlstatus != -1:
                return JsonResponse({'status': -2})
            exerz = inception.table_structure(dbaddr, dbname, sqlcontent)  # 遇到错误的语句，包括它后面的都不会执行 只检查
            # 改变本条sql的状态
            affected_rows = 0
            execute_time = 0
            opids = []
            for rz in exerz:
                rztag = rz[4]
                if rztag == 'None' or re.findall('Warning', rztag):  # 执行成功
                    ret['Warning'] = ""
                    if re.findall('Warning', rztag):
                        ret['Warning'] = rztag
                    sqlinfo.status = 0
                    # 执行结果，受影响的条数，执行所耗时间，回滚语句
                    sqlinfo.rollbackdb = rz[8]
                    affected_rows += rz[6]
                    execute_time += float(rz[9])
                    opids.append(rz[7].replace("'",""))  # rz[7].replace("'","")  : 每条sql执行后的回滚opid
                else:  # 执行失败的结果
                    sqlinfo.status = 2
                    sqlinfo.executerz = exerz
                    ret['msg'] = rztag
                    ret['status'] = -1
                    break
            sqlinfo.rollbackopid = opids
            sqlinfo.exe_affected_rows = affected_rows
            ret['affected_rows'] = affected_rows
            ret['execute_time'] = '%.3f' % execute_time  # 保留3位小数
            if username != sqlinfo.treater:  # 如果是dba或总监代执行的
                note = sqlinfo.note + '   [' + username + '代执行]'
                sqlinfo.note = note
            # mail
            if env == 1:  # 线上环境，发邮件提醒
                treater = sqlinfo.treater  # 执行人
                commiter = sqlinfo.commiter  # 提交人
                mailto_users = [treater, commiter]
                mailto_users = list(set(mailto_users))  # 去重（避免提交人和执行人是同一人，每次收2封邮件的bug）
                mailto_list = [UserProfile.objects.get(username=username).email for m in mailto_users]
                # 发送邮件，并判断结果
                mailtype = 'execute'
                send_mail.delay(mailto_list, username, sqlid, sqlinfo.note, mailtype, sqlcontent, dbname)
        elif actiontype == 'reject':
            sqlinfo.status = 1
            if username != sqlinfo.treater:
                note = sqlinfo.note + '   [' + username + '代放弃]'
                sqlinfo.note = note
        elif actiontype == 'pause':
            sqlinfo.status = -2
        elif actiontype == 'cancelpause':
            sqlinfo.status = -1
        elif actiontype == 'rollback':  # 回滚
            rollbackopid = sqlinfo.rollbackopid
            rollbackdb = sqlinfo.rollbackdb  # 回滚库
            env = sqlinfo.env
            # 根据选择的数据库环境，匹配地址
            dbobj = dbconf.objects.filter(name=dbname, env=env)[0]
            pc = prpcrypt(crykey)
            dbpasspwd = pc.decrypt(dbobj.password)
            # 拼接回滚语句
            backsqls = ''  # 回滚语句
            for opid in eval(rollbackopid)[1:]:
                # 1 从回滚总表中获取表名
                backsource = 'select tablename from $_$Inception_backup_information$_$ where opid_time = "%s" ' % opid
                backtable = inception.getbak(backsource, rollbackdb)[0][0]
                # 2 从回滚子表中获取回滚语句
                backcontent = 'select rollback_statement from %s.%s where opid_time = "%s" ' % (rollbackdb, backtable, opid)
                per_rollback = inception.getbak(backcontent)  # 获取回滚数据
                for i in per_rollback:  # 累加拼接
                    backsqls += i[0]
            # 拼接回滚语句 执行回滚操作，修改sql状态
            dbaddr = '--user=%s; --password=%s; --host=%s; --port=%s; --enable-execute;' % (dbobj.user, dbpasspwd, dbobj.host, dbobj.port)
            exerz = inception.table_structure(dbaddr, dbname, backsqls)
            sqlinfo.status = -3
            roll_affected_rows = len(exerz) - 1
            sqlinfo.roll_affected_rows = roll_affected_rows
            ret['rollnum'] = roll_affected_rows  # 执行回滚语句的结果，除去第一个use 数据库的
            if username != sqlinfo.treater:
                note = sqlinfo.note + '   [' + username + '代回滚]'
                sqlinfo.note = note
        sqlinfo.save()
        return JsonResponse(ret)

# 审核
class inception_check(LoginRequiredMixin, TemplateView):
    template_name = 'sqlmng/inception_check.html'
    # template_name = 'sqlmng/inception_check.html'
    # forbiddeneword = ['use ', ]
    # def post(self, request):
    #     webdata = QueryDict(request.body).dict()
    #     username = request.user.get_username()
    #     sqlcontent = webdata.get('sqlcontent')
    #     dbname = webdata.get('dbname')
    #     treater = webdata.get('treater')
    #     env = webdata.get('env')
    #     note = webdata.get('note')
    #     # 禁止词汇过滤
    #     for fword in self.forbiddeneword:
    #         pf = re.compile(fword, re.I)
    #         if re.search(pf, sqlcontent):
    #             return JsonResponse({'status':-1, 'fword':fword})
    #     # 根据选择的数据库环境，匹配地址
    #     dbobj = dbconf.objects.get(name=dbname, env=env)
    #     pc = prpcrypt(crykey)
    #     dbpasspwd = pc.decrypt(dbobj.password)
    #     dbaddr = '--user=%s; --password=%s; --host=%s; --port=%s; --enable-check;' % (dbobj.user, dbpasspwd, dbobj.host, dbobj.port)  # 根据数据库名 匹配其地址信息，"--check=1;" 只审核
    #     # 配置文件的inception部分
    #     sql_review = inception.table_structure(dbaddr, dbname, sqlcontent)  # 审核
    #     # 判断检测错误，有则返回
    #     errorsql = []
    #     for perrz in sql_review:
    #         if perrz[4] != 'None':
    #             errorsql.append(perrz[4])
    #     if errorsql:
    #         return JsonResponse({'status': -2, 'msg': errorsql})
    #     # 审核通过，写入数据库
    #     # 从数据库获取commiter和treater的信息（没有的话写入）
    #     utreater = UserProfile.objects.get_or_create(username = treater)  # 经理数据
    #     ucommiter = UserProfile.objects.get(username = username)  # 用户数据（是一定有的，因为他提交的SQL 所以他必然登录过了）
    #     # 写入sql信息
    #     # InceptSql 的 status 由treater操作后改写
    #     webdata['commiter'] = username
    #     sqlobj = InceptSql.objects.create(**webdata)
    #     sqlobj.sqlusers.add(utreater[0], ucommiter)
    #     if env == '1':  # 生产环境，发邮件提醒
    #         mailto_users = [username, treater, ]
    #         mailto_users = list(set(mailto_users))  # 去重（避免提交人和执行人是同一人，每次收2封邮件的bug）
    #         mailto_list = [UserProfile.objects.get(username=username).email for m in mailto_users]
    #         # 发送邮件，并判断结果
    #         mailtype = 'commit'
    #         send_mail.delay(mailto_list, username, sqlobj.id, note, mailtype, sqlcontent, dbname)
    #     return JsonResponse({'status':0})

class autoselect(LoginRequiredMixin, View):
    def post(self, request):  # 前端切换环境时，返回相应的数据（执行人，数据库名）
        webdata = QueryDict(request.body).dict()
        env = webdata.get('env')
        ret = {}
        ret['dbs'] = [db.name for db in dbconf.objects.filter(env=env)]
        userobj = request.user
        username = userobj.username
        if userobj.is_superuser:  # 超级用户，执行人是自己
            ret['managers'] = [username]
            return JsonResponse(ret)
        role = userobj.userprofile.role
        if env == '2':  # 测试环境，执行人就是自己
            managers = [username]
        elif env == '1':  # 生产环境
            if role in ['1','2'] or userobj.is_superuser:  # 经理/总监，执行人是自己
                managers = [username]
            elif role == '3':  # 研发，找出他组内的经理列表
                ug = userobj.groups.first()
                if ug:  # 用户有组
                    gusers = ug.user_set.all()
                    managers = [u.username for u in gusers if u.userprofile.role == '2']
                else:
                    managers = []
        ret['managers'] = managers
        return JsonResponse(ret)

### 优化（针对select语句，要带查询条件）
class optimize_check(LoginRequiredMixin, TemplateView):
    template_name = 'sqlmng/optimize_check.html'

    def post(self, request, **kwargs):
        webdata = QueryDict(request.body).dict()
        sqlcontent = webdata.get('sqlcontent').replace('`','')
        dbname = webdata.get('dbname')
        dbobj = dbconf.objects.get(name=dbname)
        pc = prpcrypt(crykey)
        password = pc.decrypt(dbobj.password)  # 解密
        optimizeconf = iptconf('optimize')
        toolpath = optimizeconf[1][1]
        cmd = ''' %s -h %s -u %s -p %s -P %s -v 1 -d %s  -q "%s" ''' % (toolpath, dbobj.host, dbobj.user, password, dbobj.port, dbname, sqlcontent)
        data = commands.getoutput(cmd)
        # 存db
        webdata['optimizeusers'] = request.user
        webdata['sqlcontent'] = sqlcontent
        webdata['optimizerz'] = data
        optimize.objects.create(**webdata)
        return JsonResponse({'status':0, 'data':data})

class optimize_result(LoginRequiredMixin, View):

    def get(self, request, **kwargs):
        qs = optimize.objects.all()
        page_num = request.GET.get('page', 1)  # 请求的第几页
        pageobj = JuncheePaginator(qs)
        wdata = pageobj.pagecomputer(page_num)
        return render(request, 'sqlmng/optimize_result.html', {'res_data': wdata[0], 'allpages': wdata[1]})

    def delete(self, request, **kwargs):
        pk = kwargs.get('pk')
        optimize.objects.get(id = pk).delete()
        return JsonResponse({'status':'0'})

# 数据库配置
class dbconfig(LoginRequiredMixin, ListView):
    model = dbconf
    template_name = 'sqlmng/dbconfig.html'
    paginate_by = 10
    context_object_name = 'res_data'
    #
    # def get_queryset(self):
    #     souword = self.request.GET.get('souword','')
    #     return self.model.objects.filter(name__contains=souword)
    #
    # def post(self, request, **kwargs):
    #     webdata = QueryDict(request.body).dict()
    #     dbexsit = self.model.objects.filter(name = webdata.get('name'))
    #     if dbexsit:
    #         ret = {'status':-1}
    #     else:
    #         # 取前端传来的的password
    #         password = webdata.get('password')
    #         # 对password加密
    #         pc = prpcrypt(crykey)
    #         crypassword = pc.encrypt(password)
    #         # 替换webdata的password
    #         webdata['password'] = crypassword
    #         # 写入数据库
    #         self.model.objects.create(**webdata)
    #         # 返回数据
    #         ret = {'status':0}
    #     return JsonResponse(ret)
    #
    # def delete(self, request, **kwargs):
    #     self.model.objects.get(pk=kwargs.get('pk')).delete()
    #     return JsonResponse({'status':0})
    #
    # def put(self, request, **kwargs):
    #     # 密码的修改逻辑：如果密码没变化就直接保存，有变化就加密后保存
    #     webdata = QueryDict(request.body).dict()
    #     pk = kwargs.get('pk')
    #     obj = self.model.objects.get(pk=pk)
    #     password = webdata.get('password')
    #     if obj.password != password:  # 密码被做了修改
    #         pc = prpcrypt(crykey)
    #         webdata['password'] = pc.encrypt(password)
    #     self.model.objects.filter(pk=pk).update(**webdata)
    #     return JsonResponse({'status':0})
    #

