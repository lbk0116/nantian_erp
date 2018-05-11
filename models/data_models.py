# # -*- coding: utf-8 -*-
# from openerp import models, fields, api, exceptions
# import urllib2
# import urllib
# import cookielib
# import json
#
# def get_url_content(url,session,postData):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36',
#         'Cookie': session,
#         'Accept-Encoding': 'gzip,default',
#         # 'Content-Type': 'application/json',
#     }
#     response = urllib2.urlopen(urllib2.Request(url, data=urllib.urlencode(postData), headers=headers))
#     costs = response.read()
#     if response.getcode() == 200:
#         if costs:
#             return json.loads(costs)
#         else:
#             return 0
#     else:
#         return 0
#
# #ip管理
# class ip_data(models.Model):
#     _name = 'nantian_erp.ip_data'
#     _rec_name = 'ip'
#     ip = fields.Char(string=u"IP地址")
#     port = fields.Char(string=u"IP端口",default=u'8069')
#     notes = fields.Char(string=u"说明")
#     special = fields.Char(string=u"特殊的点",default='boss')
#     admin = fields.Char(string=u"admin用户名")
#     password = fields.Char(string=u"admin密码")
#     database = fields.Char(string=u"数据库名")
#
#
# #拓展任务列
# class project_task_work(models.Model):
#     _inherit = 'project.task.work'
#     cost = fields.Float(string=u"成本" , digits=(20,2), default=0.00)
#     user_email = fields.Char(related='user_id.login', string=u'邮箱')
#
#
# #拓展任务
# class project_task(models.Model):
#     _inherit = 'project.task'
#     task_cost = fields.Float(string=u"任务成本" ,compute='_count_task_cost',store=True)
#
#     # 自动计算任务成本
#     @api.depends('work_ids.cost')
#     def _count_task_cost(self):
#         for record in self:
#             for work in record.work_ids:
#                 record.task_cost += work.cost
#
#
# #拓展项目
# class project_project(models.Model):
#     _inherit = 'project.project'
#     total_cost = fields.Float(string=u"成本总计" ,compute='_count_total_cost',store=True)
#
#     # 自动计算项目成本
#     @api.depends('tasks.task_cost')
#     def _count_total_cost(self):
#         for record in self:
#             for task in record.tasks:
#                 record.total_cost += task.task_cost
#
#     @api.multi
#     def pop_window(self,active_id):
#
#         tree_res = self.env['ir.model.data'].search([('name', '=', 'nantian_erp_project_works_tree_view'), ('module', '=', 'nantian_erp')]).res_id
#         search_id = self.env['ir.model.data'].search([('name', '=', 'nantian_erp_project_works_filter_view'), ('module', '=', 'nantian_erp')]).res_id
#         value = {
#             'name': ('项目成本列表'),
#             'res_model': 'project.task.work',
#             'views': [(tree_res, 'tree')],
#             'search_view_id': search_id,
#             'type': 'ir.actions.act_window',
#             'target': 'self',
#             'context': {'search_default_task':True},
#             'domain': [('task_id.project_id', '=', active_id)],
#         }
#         print 'qqwe'
#         return value
#
#     @api.multi
#     def get_cost(self):
#         project = {'id': self.id}
#         work = []
#         project_cost = self.env['project.project'].search([('id', '=', self.id)], limit=1)
#         for task in project_cost.tasks:
#             if task:
#                 for work_id in task.work_ids:
#                     work.append({'id': work_id.id, 'user_email': work_id.user_email, 'date': work_id.date, 'hours': work_id.hours,'cost':0})
#         project['works'] = work
#         boss_ip_data = self.env['nantian_erp.ip_data'].search([('special', '=', 'boss')], limit=1)
#         loginurl = u'http://'+boss_ip_data.ip+u':'+boss_ip_data.port+u'/web/login?db='+boss_ip_data.database
#         # 设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
#         cj = cookielib.LWPCookieJar()
#         opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#
#         urllib2.install_opener(opener)
#
#         # 登陆信息
#         loginparams = {'login': boss_ip_data.admin, 'password': boss_ip_data.password}
#         # 构造header
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'
#         }
#
#         # 需要给Post数据编码  urllib.urlencode(loginparams)
#         # 通过urllib2提供的request方法来向指定Url发送我们构造的数据，并完成登录过程
#         req = urllib2.Request(loginurl, urllib.urlencode(loginparams), headers=headers)
#         try:
#             response = urllib2.urlopen(req)
#             # 获得Cookies
#             cookies = response.headers["Set-cookie"]
#             cookie = cookies[cookies.index("session_id="):]
#             session = cookie[:cookie.index(";")]
#             #拼接网址
#             deal_ip = u'http://'+boss_ip_data.ip+u':'+boss_ip_data.port+u'/count_project_cost/'
#
#             project = json.dumps([project])
#             postdata = {'project_cost': project}
#             datas = get_url_content(deal_ip, session, postdata)
#             print datas
#             if datas:
#                 for work_id in datas:
#                     print work_id['cost']
#                     self.env['project.task.work'].search([('id', '=', work_id['id'])], limit=1).cost = work_id['cost']
#                 return self.pop_window(self.id)
#         except:
#             raise exceptions.ValidationError("由于安全限制，您无法获得所需信息，如有需要请联系服务人员")
#
#
#
