# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
from email.utils import formataddr
import email,math
from email.header import Header
from datetime import datetime,timedelta
import datetime as datetime_boss
import time
import string
import logging
import sys


sys.setrecursionlimit(1000000)


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    count = fields.Integer(string='签订次数')
    contract_sign_first = fields.Char(string = "第一阶段")
    contract_sign_second = fields.Char(string = "第二阶段")
    SN = fields.Char(string="财务序列号") #序列号
    project_cost_month_ids = fields.Many2many('nantian_erp.project_cost_month',"project_cost_month_employee_ref",string='工作组月成本表')
    performance_year_ids = fields.One2many('nantian_erp.performance_year','employee_id',string="年成本表",ondelete = 'set null')
    working_team_id = fields.Many2one('nantian_erp.working_team',string="工作组",ondelete='set null',track_visibility='onchange' )
    department_first = fields.Char(string='一级部门',compute='get_department_first',store= True)
    department_second = fields.Char(string='二级部门',compute='get_department_first',store= True)
    contract_jobs_id = fields.Many2one('nantian_erp.jobs',ondelete='set null',string='合同岗位',track_visibility='onchange',)
    nantian_erp_contract_id = fields.Many2one('nantian_erp.contract', ondelete='set null',string='服务合同', domain=[('state', '!=', 'off')],track_visibility='onchange')
    certificate_ids = fields.One2many('nantian_erp.certificate','employee_ids',ondelete = 'set null',string="证书",track_visibility='onchange')
    graduation = fields.Char(string="毕业学校",track_visibility='onchange')
    major = fields.Char(string='专业',track_visibility='onchange')
    work_time = fields.Date(string="首次工作时间",track_visibility='onchange')
    entry_time = fields.Date(string="入职时间",track_visibility='onchange')
    contract_starttime = fields.Date(string='合同开始时间',track_visibility='onchange')
    contract_endtime = fields.Date(string='合同终止时间',track_visibility='onchange')
    contract_len = fields.Integer(string='合同期限',track_visibility='onchange')
    is_forever = fields.Boolean(compute='_get_end_date',store = True,string='无期限？',track_visibility='onchange')
    education = fields.Selection(
        [
            (u'专科', u"专科"),
            (u'本科', u"本科"),
            (u'硕士', u"硕士"),
            (u'博士', u"博士"),
            (u'专升本', u"专升本"),
            (u'高级技工', u"高级技工"),
            (u'高中', u"高中"),
        ],
        string='学历(弃用)', track_visibility='onchange'
    )

    level = fields.Selection(
        [
            (u'1',1),
            (u'2',2),
            (u'3',3),
            (u'4',4),
            (u'5',5),
            (u'6',6),
            (u'7',7),
            (u'8',8),
            (u'9',9),
            (u'10',10),
            (u'11',11),
            (u'12',12),
            (u'13',13),
            (u'14',14),
            (u'15',15),
            (u'16',16)
        ],
        string='级别',track_visibility='onchange'
    )
    category = fields.Selection(
        [
            (u'公司储备', u"公司储备"),
            (u'合同在岗', u"合同在岗"),
            (u'合同备岗', u"合同备岗"),
            (u'合同赠送', u"合同赠送"),
            #(u'现场储备', u'现场储备'),
            (u'公司项目', u"公司项目"),
            (u'借出人员', u"借出人员"),
            (u'借入人员', u"借入人员"),
            (u'现场备岗', u"现场备岗"),
        ],
    default = u'公司储备', string = "人员状态",track_visibility='onchange'
    )
    specialty = fields.Text(string="特长",track_visibility='onchange')
    certificate_direction_id = fields.Many2one(related='certificate_ids.certificate_direction_id', string='证书方向',track_visibility='onchange')
    certificate_category_id = fields.Many2one(related='certificate_ids.certificate_category_id', string='证书类型',track_visibility='onchange')
    certificate_institutions_id = fields.Many2one(related='certificate_ids.certificate_institutions_id', string='证书颁发机构或者行业',track_visibility='onchange')
    certificate_level_id = fields.Many2one(related='certificate_ids.certificate_level_id', string='证书级别',track_visibility='onchange')
    work_age = fields.Integer(compute='_compute_work_age',store=True,string="工作年限",track_visibility='onchange')
    api_res = fields.Char(default="sys",string="数据来源",track_visibility='onchange')
    customer_id = fields.Many2one('res.partner', compute='_get_customer',string="客户",store=True,track_visibility='onchange')
    leave_time = fields.Date(string="离职时间",track_visibility='onchange')
    entry_age_distribute = fields.Selection(
        [
            (u'在司1年以下', u"在司1年以下"),
            (u'在司1-5年', u"在司1-5年"),
            (u'在司5-10年', u"在司5-10年"),
            (u'在司10年以上', u"在司10年以上"),

        ],
        default=u'在司1年以下', string="在司年限分布",track_visibility='onchange'
    )
    entry_len = fields.Integer(string='在司年限',track_visibility='onchange')
    phone_money = fields.Integer(string='话费额度',track_visibility='onchange')
    states = fields.Selection([
            (u'正常在岗', u"正常在岗"),
            (u'长期病假', u"长期病假"),
            (u'长期事假', u"长期事假"),
            (u'离职办理中', u"离职办理中"),
            (u'离职', u"离职"),
            (u'孕假', u"孕假"),

        ],
        default=u'正常在岗', string="工作状态",track_visibility='onchange')
    dis_states = fields.Selection([
        (u'正常', u'正常'),
        (u'待调整', u"待调整"),
        (u'可调用', u"可调用"),
        (u'申请离职', u"申请离职"),
        (u'已离职', u"已离职"),
        (u'借调中', u"借调中"),

    ], default=u'正常', string="调整状态",track_visibility='onchange')
    adjust_ids = fields.Many2many('nantian_erp.hr_adjusting','emp_to_adjust_ref',string="调整表(弃用)",ondelete='set null',track_visibility='onchange')
    adjust_dst = fields.Char(compute='get_adjust_dst', string="调整至(弃用)", store=True,track_visibility='onchange')
    work_experience_ids = fields.One2many('nantian_erp.work_experience','employee_id',string="项目经验")
    resume_id = fields.Many2one('nantian_erp.resume',string='入职简历')
    position_id = fields.Many2one('nantian_erp.job',string= '南天招聘职位')
    education_experience_ids = fields.One2many('nantian_erp.education_experience','employee_id',string='教育经历')
    leader = fields.Many2one('hr.employee',string="上一级",store=True)
    project_leader = fields.Many2one('hr.employee',string="项目负责人",store=True)

    # default=lambda self: self._get_state()
    demission_ids = fields.One2many('nantian_erp.demission','employee_id', ondelete='set null', string="离职记录之一",track_visibility='onchange')
    pers_transfer_ids = fields.One2many('nantian_erp.pers_transfer','employee_id', ondelete='set null', string="调动记录之一",track_visibility='onchange')
    formal_time = fields.Date(string="转正时间")
    test_time = fields.Integer(string="试用期")
    graduation_id = fields.Char(string="毕业证号")

    # @api.multi
    # def compute_leader(self):
    #     customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')])
    #     working_teams = self.env['nantian_erp.working_team'].search([])
    #     work_team_managers = []
    #     for working_team in working_teams:
    #         work_team_managers.append(working_team.user_id)
    #     for record in self:
    #         if record.user_id not in customer_manager_group.users:
    #             if record.customer_id:
    #                 if record.customer_id.customer_manager.employee_ids:
    #                     record.leader = record.customer_id.customer_manager.employee_ids[0]
    #             elif (record.user_id not in work_team_managers) and record.working_team_id:
    #                 if record.working_team_id.user_id and record.working_team_id.user_id.employee_ids:
    #                     record.leader = record.working_team_id.user_id.employee_ids[0]
    #             else:
    #                 record.leader = record.department_id.parent_id.manager_id
    #         else:
    #             record.leader = record.department_id.manager_id
    #     if record.leader:
    #         return record.leader


    @api.multi
    def _get_state(self):
        pro_manager = []
        dep_manager = []
        for work in self.env['nantian_erp.working_team'].search([]):
            pro_manager.append(work.user_id)
        for department in self.env['hr.department'].search([]):
            if department.manager_id:
                em = department.manager_id

                user = self.env['res.users'].search([('employee_ids', 'ilike', em.id)])

                dep_manager.append(user)
        if self.env.user not in pro_manager and self.env.user not in dep_manager:

            return 'confirmed'
        else:
            return 'done'


    # 自动导入教育经历
    @api.multi
    def import_education_experience(self):
        records = self.env['hr.employee'].search([])
        for rec in records:
            if rec.education_experience_ids:
                pass
            else:
                if rec.education == u"专科":
                    education_t = u'大专'
                elif rec.education == u"本科":
                    education_t = u"本科"
                elif rec.education == u"硕士":
                    education_t = u"硕士"
                elif rec.education == u"博士":
                    education_t = u"博士"
                elif rec.education == u"专升本":
                    education_t = u"本科"
                elif rec.education == u"高中":
                    education_t = u"高中"
                elif rec.education == u"高级技工":
                    education_t = u'大专'
                else:
                    education_t = None
                id = self.env['nantian_erp.education_experience'].create(
                    {'school': rec.graduation, 'major': rec.major, 'education': education_t, 'employee_id': rec.id})

    @api.multi
    @api.depends('department_id')
    def get_department_first(self):
        for record in self:
            if record.department_id.level == 1:
                pass
            elif record.department_id.level == 2:
                record.department_first = record.department_id.name
            elif record.department_id.level == 3:
                record.department_first = record.department_id.parent_id.name
                record.department_second = record.department_id.name
            else:
                pass

    @api.depends('adjust_ids.states')
    def get_adjust_dst(self):
        for record in self.adjust_ids:
            if record.states == u"待调整":
                self.adjust_dst = record.dst
            else:
                self.adjust_dst = ''

    @api.onchange('phone_money','level','job_id')
    def _check_phone_money(self):
        if self.phone_money:
            if self.level == '1':
                if self.job_id.name == u'助理工程师':
                    if self.phone_money != 50:

                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}
                if self.job_id.name == u'初级工程师':
                    if self.phone_money != 60:
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}
                if self.job_id.name == u'项目助理':
                    if (self.phone_money <= 60)|(self.phone_money >= 100)|(self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}
            if self.level == '2':
                if self.job_id.name == u'项目助理':
                    if (self.phone_money <= 60) | (self.phone_money >= 100) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}

                if self.job_id.name ==u'工程师':
                    if self.phone_money != 80:
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}

            if self.level == '3':
                if self.job_id.name == u'高级工程师':
                    if self.phone_money != 100:
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}


            if self.level == '4':
                if self.job_id.name == u'技术经理':
                    if (self.phone_money <= 120) | (self.phone_money >= 160) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}

                if self.job_id.name ==u'项目经理':
                    if (self.phone_money <= 120) | (self.phone_money >= 200) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}

                if self.job_id.name == u'部门副经理':
                    if (self.phone_money <= 120) | (self.phone_money >= 160) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}

            if self.level == '5':
                if self.job_id.name == u'高级技术经理':
                    if self.phone_money != 160:
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}

                if self.job_id.name == u'部门经理':
                    if (self.phone_money <= 160) | (self.phone_money >= 250) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}
            if self.level == '6':
                if self.job_id.name == u'技术总监':
                    if self.phone_money != 200:
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}

                if self.job_id.name == u'总助':
                    if (self.phone_money <= 200) | (self.phone_money >= 300) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}

            if self.level == '7':
                if self.job_id.name == u'架构师':
                    if self.phone_money != 250:
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配",
                            }}

                if self.job_id.name == u'副总经理':
                    if (self.phone_money <= 250) | (self.phone_money >= 300) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                'title': "话费额度问题",
                                'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                            }}
            if self.level == '8':
                if self.job_id.name == u'总经理':
                    if (self.phone_money <= 300) | (self.phone_money >=400) | (self.phone_money % 10 != 0):
                        return {
                            'warning': {
                                           'title': "话费额度问题",
                                           'message': "话费额度与级别职位不匹配或者话费额度不是10的倍数",
                                       }}

    @api.multi
    def onchange_category(self,category):
        result = {'value': {}}
        if category==u"公司储备" or category==u"公司项目":

            result['value']['nantian_erp_contract_id'] = ''
            result['value']['contract_jobs_id'] = ''
        return result


    @api.depends('working_team_id.partner_id')
    def _get_customer(self):
        for record in self:
            if record.working_team_id:
                record.customer_id=record.working_team_id.partner_id

    # 计算工作年限
    @api.one
    @api.depends('work_time')
    def _compute_work_age(self):
        for record in self:
            if record.work_time:
                now=fields.datetime.now()
                work_time = fields.Datetime.from_string(record.work_time)
                months = int(str(now.month))-int(str(work_time.month))
                days =int(str(now.day)) - int(str(work_time.day))
                if months<0 or (months == 0 and days<0):
                    record.work_age=int(str(now.year))-int(str(work_time.year))-1
                else:
                    record.work_age = int(str(now.year)) - int(str(work_time.year))
    #计算工作年限
    @api.multi
    def action_to_compute_work_age(self):
        recs = self.env['hr.employee'].search([])
        for record in recs:
            if record.work_time:
                now = fields.datetime.now()
                work_time = fields.Datetime.from_string(record.work_time)
                months = int(str(now.month)) - int(str(work_time.month))
                days = int(str(now.day)) - int(str(work_time.day))
                if months < 0 or (months == 0 and days < 0):
                    record.work_age = int(str(now.year)) - int(str(work_time.year)) - 1
                else:
                    record.work_age = int(str(now.year)) - int(str(work_time.year))

    #计算在司年限
    @api.multi
    def action_to_compute_entry_age(self):
        recs = self.env['hr.employee'].search([])
        for record in recs:
            if record.entry_time:
                now = fields.datetime.now()
                entry_len = fields.Datetime.from_string(record.entry_time)
                months = int(str(now.month)) - int(str(entry_len.month))
                days = int(str(now.day)) - int(str(entry_len.day))
                if months < 0 or (months == 0 and days < 0):
                    record.entry_len = int(str(now.year)) - int(str(entry_len.year)) - 1
                else:
                    record.entry_len = int(str(now.year)) - int(str(entry_len.year))
                if record.entry_len < 1:
                    record.entry_age_distribute = u'在司1年以下'
                elif record.entry_len >= 1 and record.entry_len < 5:
                    record.entry_age_distribute = u'在司1-5年'
                elif record.entry_len >= 5 and record.entry_len < 10:
                    record.entry_age_distribute = u'在司5-10年'

                else:
                    record.entry_age_distribute = u'在司10年以上'

    # # 计算合同截止日期
    @api.one
    @api.depends('contract_starttime', 'contract_len','is_forever')
    def _get_end_date(self):
        if not self.is_forever:
            if not (self.contract_starttime and self.contract_len):
                self.contract_endtime = self.contract_starttime
                return
            start=fields.Datetime.from_string(self.contract_starttime)
            # self.contract_endtime =datetime(start.year+self.contract_len,start.month,start.day)
        # else:
            # self.contract_endtime='9999-12-31'

    #与招聘系统对接函数,通过员工创建用户,并关联
    @api.multi
    def hr_to_user(self):
        recs = self.env['hr.employee'].search([('api_res', '=', 'web_api'), ('user_id', '=', None)])
        group_hr_id = self.env['ir.model.data'].search(
            [('name', '=', 'group_hr_user'), ('module', '=', 'nantian_erp')]).res_id
        hr_id = self.env['res.groups'].search([('id', '=', group_hr_id)])
        for rec in recs:
            old_user = self.env['res.users'].search([('login','=', rec.work_email)])
            if old_user:
                user = old_user
            else:
                user = self.env['res.users'].create(
                {'login': rec.work_email, 'password': '123456', 'name': rec.name,'email':rec.work_email})
            rec.user_id = user
            hr_id.users |= user

    @api.multi
    def add_use_to_group(self):
        users = self.env['res.users'].search([('active','=',True)])
        data_center_employee_group = self.env['res.groups'].search([('name', '=', u'人力-数据中心员工')])
        employee_group = self.env['res.groups'].search([('name', '=', u'人力-其他部门员工')])
        customer_managers_obj = self.env['res.partner'].search([('category','=',u'服务客户')])
        customer_managers_ids=[]
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')])
        for i in customer_managers_obj:
            customer_managers_ids.append(i.customer_manager.id)
        # print'行业负责人',customer_managers_ids
        customer_managers = self.env['res.users'].search([('id','in',customer_managers_ids)])
        customer_manager_group.users |= customer_managers
        bm_managers_obj = self.env['hr.department'].search([('parent_id.parent_id.name', '=', u'集成服务事业部'),('parent_id.name', '!=', u'数据中心服务部'),('name', '!=',u'数据中心服务部')])
        bm_managers_group = self.env['res.groups'].search([('name', '=', u'人力-部门经理')])
        bm_managers_ids = []
        for i in bm_managers_obj:
            if i.manager_id.user_id:
                bm_managers_ids.append(i.manager_id.user_id.id)
        print'部门经理', bm_managers_ids
        bm_managers = self.env['res.users'].search([('id','in',bm_managers_ids)])
        if bm_managers:
            bm_managers_group.users |= bm_managers
        managers_obj = self.env['hr.department'].search([('parent_id.name', '=', u'集成服务事业部')])
        manager_group = self.env['res.groups'].search([('name', '=', u'总经理')])
        managers_ids=[]
        for i in managers_obj:
            if i.manager_id.user_id:
                managers_ids.append(i.manager_id.user_id.id)
        # print '总经理', managers_ids
        managers = self.env['res.users'].search([('id','in',managers_ids)])
        # print managers
        manager_group.users |= managers
        presidents = self.env['hr.department'].search([('name', '=', u'集成服务事业部')],limit=1)
        president_group = self.env['res.groups'].search([('name', '=', u'总裁')])
        if presidents.manager_id.user_id:
            president_group.users |= presidents.manager_id.user_id
            # print '总裁',presidents.manager_id.user_id
        data_center_employees_ids = []
        data_employees = self.env['hr.employee'].search(['|',('department_id.name','=',u'数据中心服务部'),('department_id.parent_id.name','=',u'数据中心服务部')])
        #print data_employees
        for i in data_employees:
            if i.user_id:
                # print i.user_id
                data_center_employees_ids.append(i.user_id.id)
        #print '数据中心员工',data_center_employees_ids
        data_center_employees = self.env['res.users'].search([('id','in',data_center_employees_ids)])
        data_center_employee_group.users |= data_center_employees
        other_employees_ids = []
        employees = self.env['hr.employee'].search([('department_id.name','!=',u'数据中心服务部'),('department_id.parent_id.name','!=',u'数据中心服务部'),('department_id.name','!=',u'集成服务事业部')])
        # print '&'*80
        for i in employees:
            if i.user_id:
                # print i.user_id
                other_employees_ids.append(i.user_id.id)
        #print '其他部门员工',other_employees_ids
        other_employees = self.env['res.users'].search([('id','in',other_employees_ids)])
        employee_group.users |= other_employees
        print '#'*80

    @api.multi
    @api.depends('customer_id','working_team_id','department_first')
    def compute_leader(self):
        customer_manager_group = self.env['res.groups'].search([('name', '=', u'行业负责人')])
        working_teams = self.env['nantian_erp.working_team'].search([])
        work_team_managers = []
        for working_team in working_teams:
            work_team_managers.append(working_team.user_id)
        for record in self:
            if record.job_id and (record.job_id.name == "副总经理" or \
                      record.job_id.name == "副总经理" or record.job_id.name == "副总经理"):
                record.leader = record.department_id.parent_id.manager_id
            elif record.user_id not in customer_manager_group.users:
                if record.customer_id:
                    if record.customer_id.customer_manager.employee_ids:
                        record.leader = record.customer_id.customer_manager.employee_ids[0]
                elif (record.user_id not in work_team_managers) and record.working_team_id:
                    if record.working_team_id.user_id and record.working_team_id.user_id.employee_ids:
                        record.leader = record.working_team_id.user_id.employee_ids[0]
                else:
                    record.leader = record.department_id.parent_id.manager_id
            else:
                record.leader = record.department_id.manager_id


#证书
class certificate(models.Model):
    _name = 'nantian_erp.certificate'
    _rec_name = 'name'
    name = fields.Char(related='certificate_direction_id.name', store=True)
    certificate_direction_id = fields.Many2one('nantian_erp.certificate_direction',string='方向')
    certificate_category_id = fields.Many2one('nantian_erp.certificate_category', string='认证类型')
    certificate_institutions_id = fields.Many2one('nantian_erp.certificate_institutions', string='颁发机构或行业')
    certificate_level_id = fields.Many2one('nantian_erp.certificate_level', string='级别')
    time = fields.Date(placeholder="截止日期",string="有效期")
    is_forever_validate = fields.Boolean(string="是否长期有效",default = False)
    employee_ids = fields.Many2one('hr.employee',ondelete='set null')
    image = fields.Binary(string='证书扫描件')

    #当选中永久时修改证书时限
    @api.multi
    def onchange_time(self,is_forever_validate):
        result = {'value': {}}
        if is_forever_validate:
            result['value']['time'] = datetime(9999,12,31)
        return result
    #证书过期提醒
    def expiration_reminder(self, cr, uid, erp_server_addr, context=None):
        '''
        证书过期提醒。
        每天执行一次，检测当天到期的证书，给证书主人及其上级发送一封到期提醒邮件。
        重复执行的设置钩子，在【设置】-【技术】-【自动化】-【安排的动作】里增加一条每天执行一次的动作。
        设置需要一个参数，表示邮件里用于用户点击的链接。
        另外，需要设置出去的邮件服务器.
        '''
        log_line_head = "### zhengshu daoqi tixing: "
        exp_cers_ids = self.search(cr, uid, [("time", "=", time.strftime("%Y-%m-%d"))], context=context)
        exp_cers = self.browse(cr, uid, exp_cers_ids, context=context)

        dai_fa_song = {}  # format:
        # {hr_employee.id: {obj: hr_employee
        #                   users: {hr_employee.id: {obj: hr_employee
        #                                            cers: [nantian_erp.certificate]
        #                                           }
        #                          }
        #                   }
        # }

        for cer in exp_cers:
            if not cer.employee_ids:
                continue
            user = cer.employee_ids
            mgr = None
            mgr_id = None
            if user.parent_id:
                mgr = user.parent_id
                mgr_id = mgr.id
            if not dai_fa_song.has_key(mgr_id):
                dai_fa_song[mgr_id] = {
                    "obj": mgr,
                    "users": {}
                }
            if not dai_fa_song[mgr_id]["users"].has_key(user.id):
                dai_fa_song[mgr_id]["users"][user.id] = {
                    "obj": user,
                    "cers": []
                }
            dai_fa_song[mgr_id]["users"][user.id]['cers'].append(cer)

        failed_users = []

        for mid, mgr in dai_fa_song.items():
            users = mgr['users']
            mgr = mgr['obj']
            if mgr != None:
                if not mgr.work_email:
                    failed_users.append(mgr)
                else:
                    to_list = [formataddr((Header(mgr.name_related, "utf8").encode(), mgr.work_email.encode("utf8")))]
                    mail_content = u"<div>%s 您好:" \
                                   u"<p>您的下属中有如下成员证书已经到期，特此提醒。</p>" \
                                   u"<ol>%s</ol>" \
                                   u"<p>详情请登录南天ERP查询：<a href='%s'>%s</a></p>" \
                                   u"<p>南天电子</p></div>" \
                        %(mgr.name_related,
                        "".join([u"<li>%s 证书【%s】到期时间 %s 。</li>" %(user['obj'].name_related, c.name, c.time)
                            for user_id, user in users.items() for c in user["cers"]]),
                        erp_server_addr, erp_server_addr)
                    mail_mail = self.pool.get('mail.mail')
                    mail_id = mail_mail.create(cr, uid, {
                        'body_html': mail_content,
                        'subject': Header(u'证书过期提醒', 'utf-8').encode(),
                        'email_to': to_list,
                        'auto_delete': True,
                    }, context=context)
                    # print("%s sending to %s(%s)..." %(log_line_head, mgr.name_related, mgr.work_email))
                    mail_mail.send(cr, uid, [mail_id], context=context)

            for user_id, user in users.items():
                cers = user['cers']
                user = user['obj']
                if not user.work_email:
                    failed_users.append(user)
                    continue
                to_list = [formataddr((Header(user.name_related, "utf8").encode(), user.work_email.encode("utf8")))]
                mail_content = u"<div>%s 您好：" \
                               u"<p>您有如下证书已经到期：</p>" \
                               u"<ol>%s</ol>" \
                               u"<p>详情请登录南天ERP查询：<a href='%s'>%s</a></p>" \
                               u"<p>南天电子</p></div>" \
                    %(user.name_related,
                    "".join([u"<li>%s 到期时间 %s</li>" % (c.name, c.time) for c in cers]),
                    erp_server_addr, erp_server_addr)

                mail_mail = self.pool.get('mail.mail')
                mail_id = mail_mail.create(cr, uid, {
                    'body_html': mail_content,
                    'subject': Header(u'证书过期提醒', 'utf-8').encode(),
                    'email_to': to_list,
                    'auto_delete': True,
                }, context=context)
                # print("%s sending to %s(%s)..." %(log_line_head, user.name_related, user.work_email))
                mail_mail.send(cr, uid, [mail_id], context=context)

        # if failed_users:
        #     print("%s send failed users(email is empty): %s items. [%s]" %(log_line_head, len(failed_users),
        #         ", ".join(["%s(%s)" %(user.name_related, user.id) for user in failed_users])))
        # print(dai_fa_song)


#证书--认证类型
class certificate_category(models.Model):
    _name = 'nantian_erp.certificate_category'
    _rec_name = 'name'
    name = fields.Char(required=True, string='认证类型')
#证书--机构
class certificate_institutions(models.Model):
    _name = 'nantian_erp.certificate_institutions'
    _rec_name = 'name'
    name = fields.Char(string='机构')
    category_id = fields.Many2one('nantian_erp.certificate_category', string='认证类型',ondelete='set null', select=True)
#证书--方向
class certificate_direction(models.Model):
    _name = 'nantian_erp.certificate_direction'
    _rec_name = 'name'
    name = fields.Char(string='方向')
    institutions_id = fields.Many2one('nantian_erp.certificate_institutions', string='机构',ondelete='set null', select=True)
#证书--级别
class certificate_level(models.Model):
    _name = 'nantian_erp.certificate_level'
    _rec_name = 'name'
    name = fields.Char(string='级别')
    direction_id = fields.Many2one('nantian_erp.certificate_direction',string='方向', ondelete='set null', select=True)

#员工离职
class hr_dimission(models.Model):
    _name = 'nantian_erp.hr_dimission'

    employee_ids = fields.Many2one('hr.employee', ondelete='set null',default=lambda self: self.env.user.employee_ids[0])
    dimission_why = fields.Selection(
        [
            (u'薪资待遇不满意', u"薪资待遇不满意"),
            (u'工作环境不满意', u"工作环境不满意"),
            (u'工作发展方向不满意', u"工作发展方向不满意"),
            (u'有更好的公司选择', u"有更好的公司选择"),
            (u'家庭原因', u"家庭原因"),
            (u'身体原因', u'身体原因'),
            (u'其他', u'其他'),
        ],
        string="离职原因")
    dimission_goto = fields.Text(string="离职去向")
    dimission_date = fields.Date(string = "离职时间")
    dimission_why_add = fields.Text(string="其他原因")
    state = fields.Selection(
        [
            ('application', u'离职申请'),
            ('check', u'审批'),
            ('again_check', u'总经理审批'),
            ('done', u'完成'),
            ('no',u'拒绝'),
        ],
        default='application', string="离职申请状态")
    dealer = fields.Many2one('res.users',string="处理人")
    hr_officer = fields.Many2one('hr.employee',string="审批人")
    hr_officer_user = fields.Many2one(related='hr_officer.user_id',string="审批人用户")
    hr_manager = fields.Many2one('hr.employee',string="最终审批人")
    hr_manager_user = fields.Many2one(related='hr_manager.user_id',string="最终审批人用户")

    #工作流创建时执行的函数
    @api.multi
    def dimission_apply(self):
        '''
        判断该员工是否满足离职申请条件----有无相应领导审批
        如果有--修改申请状态并添加审批人
        如果没有--警告创建不予成功
        '''
        if  self.employee_ids.department_id.manager_id:
            self.employee_ids.states = u'离职办理中'
            if self.env['res.users'].search([('employee_ids', 'ilike', self.employee_ids.department_id.manager_id.id)],
                                            limit=1) in self.env['res.groups'].search([('name', '=', "Manager"),('category_id.name','=','Human Resources')]).users:
                self.hr_manager = self.employee_ids.department_id.manager_id
                self.state = 'application'
            elif self.employee_ids.department_id.manager_id == self.employee_ids:
                self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
                self.state = 'application'
            else:

                self.hr_officer = self.employee_ids.department_id.manager_id
                if self.employee_ids.department_id.parent_id.manager_id:
                    self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
                    self.state = 'application'
                else:
                    raise exceptions.ValidationError('您需要一个总经理去处理您的离职申请')
        else:
            raise exceptions.ValidationError('您没有经理去处理您的离职申请')
    #工作流中转总经理审批函数
    def dimission_check(self):
        if self.hr_manager:
            if self.hr_officer:
                self.state = 'check'
                self.dealer = self.hr_officer_user
            else:
                self.state = 'again_check'
                self.dealer = self.hr_manager_user

    # 工作流中转经理审批函数
    def dimission_again_check(self):
        self.state = 'again_check'
        self.dealer = self.hr_manager_user
    #工作流--完成函数
    @api.multi
    def dimission_done(self):
        self.state = 'done'
        self.dealer = self.env.user
        self.employee_ids.active = 0
        self.employee_ids.user_id.active = 0
        self.employee_ids.leave_time = self.dimission_date
        self.employee_ids.states = u'离职'
    #工作流--拒绝函数
    def dimission_no(self):
        self.state = 'no'
        self.employee_ids.states = u'正常在岗'

# class hr_attendance(models.Model):
#     _inherit = 'hr.attendance'
#
#     state = fields.Selection([
#          ('draft', "新建"),
#          ('confirmed', "待确认"),
#          ('done', "已确认"),
#     ], default=lambda self: self._get_state())
#     examine_user = fields.Many2one('res.users',string='审批人',default=lambda self: self._get_examine_user())
#
#     @api.multi
#     def _get_state(self):
#         pro_manager = []
#         dep_manager = []
#         for work in self.env['nantian_erp.working_team'].search([]):
#             pro_manager.append(work.user_id)
#         for department in self.env['hr.department'].search([]):
#             if department.manager_id:
#                 em = department.manager_id
#
#                 user = self.env['res.users'].search([('employee_ids', 'ilike', em.id)])
#
#                 dep_manager.append(user)
#         if self.env.user not in pro_manager and self.env.user not in dep_manager:
#
#             return 'confirmed'
#         else:
#             return 'done'
#
#     @api.multi
#     def _get_examine_user(self):
#         pro_manager = []
#         dep_manager = []
#         for work in self.env['nantian_erp.working_team'].search([]):
#             pro_manager.append(work.user_id)
#         for department in self.env['hr.department'].search([]):
#             if department.manager_id:
#                 em = department.manager_id
#                 user = self.env['res.users'].search([('employee_ids', 'ilike', em.id)])
#                 dep_manager.append(user)
#         if self.env.user not in pro_manager and self.env.user not in dep_manager:
#             if self.env.user.employee_ids.parent_id:
#                 return self.env.user.employee_ids.parent_id.user_id
#             else:
#                 return None
#         else:
#             return None
#     @api.one
#     def action_draft(self):
#         self.state = 'draft'
#         self.examine_user = self.employee_id.user_id
#
#     @api.one
#     def action_confirm(self):
#         self.state = 'confirmed'
#         self.examine_user = self.employee_id.user_id.employee_ids[0].parent_id.user_id
#
#     @api.one
#     def action_done(self):
#         self.state = 'done'

#员工请假
class hr_leave(models.Model):
    _name = 'nantian_erp.hr_leave'
    name = fields.Char(string='请假单',)
    state = fields.Selection(
        [
            ('application', u'请假申请'),
            ('check', u'审批'),
            ('again_check', u'总经理审批'),
            ('done', u'完成'),
            ('no', u'拒绝'),
        ],
        default='application', string="离职申请状态")
    dealer = fields.Many2one('res.users', string="处理人")
    hr_officer = fields.Many2one('hr.employee', string="审批人")
    hr_officer_user = fields.Many2one(related='hr_officer.user_id', string="审批人用户")
    hr_manager = fields.Many2one('hr.employee', string="最终审批人")
    hr_manager_user = fields.Many2one(related='hr_manager.user_id', string="最终审批人用户")
    employee_ids = fields.Many2one('hr.employee', string="申请人",ondelete='set null',default=lambda self: self.env.user.employee_ids[0])
    leave_type = fields.Many2one('nantian_erp.hr_leave_type', string="请假类型")
    date_from = fields.Datetime(string="开始日期")
    date_to = fields.Datetime(string="结束日期")
    reason = fields.Text(string="请假原因")

    #审批邮件发送函数
    def send_email(self, cr, uid, users, body='', subject='', context=None):
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name, 'utf-8').encode(), user.email)))
        mail_mail = self.pool.get('mail.mail')
        mail_id = mail_mail.create(cr, uid, {
            'body_html': body,
            'subject': subject,
            'email_to': to_list,
            'auto_delete': True,
        }, context=context)
        mail_mail.browse(cr, uid, [mail_id], context=context).email_from = '南天ERP系统<nantian_erp@nantian>'
        mail_mail.send(cr, uid, [mail_id], context=context)

    #工作流创建函数
    @api.multi
    def leave_apply(self):
        '''
        根据条件判断是否可以创建申请---有无领导审批
        有--判断人员身份及请假类型进行不同状态改变及审批流程
        没有--警告  创建失败
        '''
        if self.env.user in self.env['res.groups'].search(
                [('name', '=', "Manager"), ('category_id.name', '=', 'Human Resources')]).users:
            self.state = 'done'
        elif self.employee_ids.child_ids or self.env.user in self.env[
            'nantian_erp.working_team'].user_id or self.employee_ids == self.employee_ids.department_id.manager_id:
            if self.leave_type.name == u"调休":
                print """yes"""
                self.state = 'done'
            elif self.env['res.users'].search(
                    [('employee_ids', 'ilike', self.employee_ids.department_id.manager_id.id)], limit=1) in self.env[
                'res.groups'].search([('name', '=', "Manager"), ('category_id.name', '=', 'Human Resources')]).users:

                self.hr_manager = self.employee_ids.department_id.manager_id
                self.state = 'application'
            elif self.env['res.users'].search(
                    [('employee_ids', 'ilike', self.employee_ids.department_id.parent_id.manager_id.id)], limit=1) in \
                    self.env['res.groups'].search(
                            [('name', '=', "Manager"), ('category_id.name', '=', 'Human Resources')]).users:
                self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
                self.state = 'application'
            else:
                raise exceptions.ValidationError('您需要一个总经理去处理您的请假申请')
        elif self.employee_ids.parent_id:
            print "haolai"
            if self.env['res.users'].search([('employee_ids', 'ilike', self.employee_ids.parent_id.id)], limit=1) in \
                    self.env['res.groups'].search([('name', '=', "Manager"), (
                            'category_id.name', '=', 'Human Resources')]).users:
                if self.leave_type.name == u"调休":
                    self.state = 'done'
                else:
                    self.hr_manager = self.employee_ids.parent_id
            else:
                if self.leave_type.name == u"调休":
                    self.hr_officer = self.employee_ids.parent_id
                else:
                    self.hr_officer = self.employee_ids.parent_id
                    self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
            self.state = 'application'
        elif not self.employee_ids.parent_id and self.employee_ids.department_id.manager_id:
            if self.leave_type.name == u"调休":
                self.hr_officer = self.employee_ids.department_id.manager_id
            elif self.env['res.users'].search(
                    [('employee_ids', 'ilike', self.employee_ids.department_id.manager_id.id)], limit=1) in self.env[
                'res.groups'].search([('name', '=', "Manager"), ('category_id.name', '=', 'Human Resources')]).users:

                self.hr_manager = self.employee_ids.department_id.manager_id
            elif self.env['res.users'].search(
                    [('employee_ids', 'ilike', self.employee_ids.department_id.parent_id.manager_id.id)], limit=1) in \
                    self.env['res.groups'].search(
                            [('name', '=', "Manager"), ('category_id.name', '=', 'Human Resources')]).users:
                self.hr_officer = self.employee_ids.department_id.manager_id
                self.hr_manager = self.employee_ids.department_id.parent_id.manager_id
            self.state = 'application'
        else:
            raise exceptions.ValidationError('您没有经理或者上级去处理您的请假申请')
    #工作流判断是否执行函数
    @api.multi
    def judge_check(self):
        if self.hr_officer:
            return True
        return False

    # 工作流判断是否执行函数
    @api.multi
    def judge_again(self):
        if self.hr_manager and not self.hr_officer:
            return True
        return False
    #工作流审批中转函数
    def leave_check(self):
        if self.hr_manager:
            if self.hr_officer:
                self.state = 'check'
                self.dealer = self.hr_officer_user
            else:
                self.state = 'again_check'
                self.dealer = self.hr_manager_user
        else:
            if self.hr_officer:
                self.state = 'check'
                self.dealer = self.hr_officer_user
        body = u'<div><p>您好:</p><p>你有一份请假申请需要审批,您可登录：<a href="http://123.56.147.94:8000/web?#page=0&limit=80&view_type=list&model=nantian_erp.hr_leave&menu_id=734&action=1077">http://123.56.147.94:8000</a>查看详细信息</p>'+u'<p>申请人：'+self.employee_ids.name+u'</p>'+u'</div>'
        subject ='请假申请'
        self.send_email(self.dealer, body, subject)

    #工作流审批总经理中转函数
    def leave_again_check(self):
        if self.hr_manager:
            self.state = 'again_check'
            self.dealer = self.hr_manager_user
        else:
            if self.hr_officer:
                self.state = 'done'
        body = u'<div><p>您好:</p><p>你有一份请假申请需要审批,您可登录：<a href="http://123.56.147.94:8000/web?#page=0&limit=80&view_type=list&model=nantian_erp.hr_leave&menu_id=734&action=1077">http://123.56.147.94:8000</a>查看详细信息</p>'+u'<p>申请人：'+self.employee_ids.name+u'</p>'+u'</div>'
        subject = '请假申请'
        self.send_email(self.dealer, body, subject)
    #工作流--请假批准函数
    def leave_done(self):
        self.state = 'done'
        body = '<div><p>您好:</p><p>你的请假申请已经通过，您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a>查看详细信息</p></div>'
        subject = '请假申请通过'
        self.send_email(self.employee_ids.user_id , body, subject)
    #工作流--请假拒绝函数
    def leave_no(self):
        self.state = 'no'
        body = '<div><p>您好:</p><p>你的请假申请被拒绝,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a>查看详细信息</p></div>'
        subject = '请假申请被拒绝'
        self.send_email(self.employee_ids.user_id, body, subject)
    #请假日期自动从开始日期加8小时作为结束日期---执行一次
    @api.multi
    def onchange_date_from(self, date_to, date_from):

        if (date_from and date_to) and (date_from > date_to):
            raise exceptions.ValidationError("结束日期必须大于开始日期")

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.strptime(date_from,
                                                            tools.DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        # if (date_to and date_from) and (date_from <= date_to):
        #     diff_day = self._get_number_of_days(date_from, date_to)
        #     result['value']['number_of_days'] = round(math.floor(diff_day)) + 1
        # else:
        #     result['value']['number_of_days'] = 0

        return result
    #请假日期自动从开始日期加8小时作为结束日期---执行一次
    @api.multi
    def onchange_date_to(self, date_to, date_from):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise exceptions.ValidationError("结束日期必须大于开始日期")

        result = {'value': {}}

        # Compute and update the number of days
        # if (date_to and date_from) and (date_from <= date_to):
        #     diff_day = self._get_number_of_days(date_from, date_to)
        #     result['value']['number_of_days'] = round(math.floor(diff_day)) + 1
        # else:
        #     result['value']['number_of_days'] = 0

        return result
#员工请假类型
class hr_leave_type(models.Model):
    _name = 'nantian_erp.hr_leave_type'
    name = fields.Char(string='请假类型')

#南天合同--岗位
class jobs(models.Model):
    _name = 'nantian_erp.jobs'

    name = fields.Char(string='岗位名称')
    contract_id = fields.Many2one('nantian_erp.contract', string="合同")
    instruction = fields.Text(string='岗位说明')
    price = fields.Float(string = '单价(人/时间)')
    unit = fields.Selection(
        [
            ('year', u'人/年'),
            ('month',u'人/月'),
            ('days', u'人/天'),
            ('days', u'人/小时'),
        ],
        string="计量单位", default='year'
    )
    amount = fields.Integer(string='人员数量', default=1)
    unit_amount = fields.Float(string='时间数量', digits=(20,3), default=1.000)
    rate = fields.Selection(
        [
            ('0.00',u'0%'),
            ('0.06',u'6%'),
            ('0.11', u'11%'),
            ('0.17', u'17%')
        ],
        string="税率", default='0.00'
    )
    rated_moneys=fields.Float(compute='_count_rated_moneys', store=True, string ="税金")
    employee_ids = fields.One2many('hr.employee', 'contract_jobs_id', "Employees")
    subtotal = fields.Float(compute='_count_subtotal', store=True,string="小计")
    employee_count = fields.Integer(compute='_count_employees', store=True)

    # 自动计算关联人数
    @api.depends('employee_ids')
    def _count_employees(self):
        for record in self:
            record.employee_count = len(record.employee_ids)

    # 小计自动计算
    @api.depends('price','amount','unit_amount')
    def _count_subtotal(self):
        for record in self:
            if record.amount and record.unit_amount:
                record.subtotal = record.price*record.amount*record.unit_amount
            else:
                raise exceptions.ValidationError("人员数量不能小于1,时间数量不能为0")
    #税金自动计算
    @api.depends('price','amount','rate','unit_amount')
    def _count_rated_moneys(self):
        for record in self:
            if record.amount and record.unit_amount:
                pass
            else:
                raise exceptions.ValidationError("人员数量不能小于1,时间数量不能为0")
            if record.rate:
                record.rated_moneys = record.price * record.amount * record.unit_amount / (string.atof(record.rate) + 1) * string.atof(record.rate)
    #修改作为外键时的显示
    @api.multi
    @api.depends('name', 'contract_id')
    def name_get(self):
        datas=[]
        for r in self:
            if r.contract_id :
                datas.append((r.id, (r.contract_id.name+'_'+r.name + '_'+ u'岗位要求人数' + unicode(r.amount) + u'人')))
            else:
                datas.append((r.id, (r.name+'--' + u'岗位要求人数' + unicode(r.amount) + u'人')))
        return datas


#南天维保合同--明细
class detail(models.Model):
    _name = 'nantian_erp.detail'
    name = fields.Char(string='名称')
    contract_id = fields.Many2one('nantian_erp.contract', string="合同")
    instruction = fields.Text(string='说明')
    price = fields.Float(string = '单价')
    unit = fields.Selection(
        [
            ('other', u'其他'),
        ],
        string="单位", default='other'
    )
    amount = fields.Integer(string='数量', default=1)
    rate = fields.Selection(
        [
            ('0.00',u'0%'),
            ('0.06',u'6%'),
            ('0.11', u'11%'),
            ('0.17', u'17%')
        ],
        string="税率", default='0.00'
    )
    rated_moneys=fields.Float(compute='_count_rated_moneys', store=True, string ="税金")
    subtotal = fields.Float(compute='_count_subtotal', store=True,string="小计")
    #小计自动计算
    @api.depends('price','amount')
    def _count_subtotal(self):
        for record in self:
            if record.amount:
                record.subtotal = record.price*record.amount
            else:
                raise exceptions.ValidationError("数量不能小于1")
    #税金自动计算
    @api.depends('price','amount','rate')
    def _count_rated_moneys(self):
        for record in self:
            if record.amount:
                pass
            else:
                raise exceptions.ValidationError("数量不能小于1")
            if record.rate:
                record.rated_moneys = record.price * record.amount / (string.atof(record.rate) + 1) * string.atof(record.rate)
    #修改作为外键时的显示
    @api.multi
    @api.depends('name', 'instruction')
    def name_get(self):
        datas=[]
        for r in self:
            if r.instruction:
                datas.append((r.id, (r.name + '(' + (r.instruction) + ')')))
            else:
                datas.append((r.id, (r.name)))
        return datas


#南天合同--收款
class collection(models.Model):
    _name = 'nantian_erp.collection'
    name = fields.Char(string='名称')
    contract_id = fields.Many2one('nantian_erp.contract', string="合同")
    date = fields.Date(string='合同收款时间')
    materials_date = fields.Date(string='准备合同材料收款时间')
    project_gathering_id = fields.Many2one('nantian_erp.project_gathering', string="项目收款")
    evaluate_money = fields.Float(string='预期收款金额')
    conditions = fields.Text(string='收款前提条件')
    money = fields.Float(string='实际收款金额')
    rate = fields.Selection(
        [
            ('0.00', u'0%'),
            ('0.06', u'6%'),
            ('0.11', u'11%'),
            ('0.17', u'17%')
        ],
        string="税率", default='0.00'
    )
    rated_moneys = fields.Float(compute='_count_rated_moneys', store=True, string="税金")
    money_total = fields.Float(compute='_count_money_total', store=True, string="不含税收款金额")
    state = fields.Selection(
        [
            (u'创建中', u'创建中'),
            (u'未收款', u'未收款'),
            (u'已收款', u'已收款'),
        ],
        string="收款状态", compute='_change_state',default=u'创建中',store=True
    )
    user_id = fields.Many2one('res.users',compute='_change_state', string="操作人", store=True)
    time = fields.Datetime(compute='_change_state',string='确认时间' )
    actually_collection_time = fields.Date(string="实际收款时间")

    #自动计算税金
    @api.depends('money', 'rate')
    def _count_rated_moneys(self):
        for record in self:
            if record.rate:
                record.rated_moneys = record.money / (string.atof(record.rate)+1)*string.atof(record.rate)
    #自动计算税前金额
    @api.depends('money', 'rated_moneys')
    def _count_money_total(self):
        for record in self:
            record.money_total = record.money - record.rated_moneys
    #根据收款金额自动修改状态并记录操作时间
    @api.multi
    @api.depends('evaluate_money', 'money')
    def _change_state(self):
        for record in self:
            if record.evaluate_money and not record.money:
                record.state = u'未收款'
            if record.money:
                record.state = u'已收款'
                record.user_id = self.env.user
                record.time = fields.datetime.now()

    @api.multi
    @api.depends('name', 'contract_id')
    def name_get(self):
        datas = []
        for r in self:
            if r.contract_id:
                datas.append((r.id, (r.contract_id.name+'_'+r.name)))
            else:
                datas.append((r.id, r.name))
        return datas


# 南天合同
class contract(models.Model):
    _name = 'nantian_erp.contract'
    name = fields.Char(string='合同名称',required=True)
    contract_num = fields.Char(string = '合同号',required =True)
    header_id = fields.Many2one('res.users', string="合同负责人",default=lambda self: self.env.user)
    other_header_id = fields.Many2one('res.users', string="合同共同负责人")
    customer_id = fields.Many2one('res.partner', string="客户",domain="[('category','=',u'服务客户')]")
    date_start = fields.Date(string="开始日期")
    date_end = fields.Date(string="结束日期")
    need_employee_count = fields.Integer(compute='_need_count_employees', string="合同约定人数",store=True)
    employee_count = fields.Integer(compute='_count_employees', string='现场人数',store=True)
    is_need = fields.Boolean(compute='_count_is_need',string='缺员',store=True)
    employee_jobs_count = fields.Integer(compute='_count_employees_jobs', string='现场合同岗位人数', store=True)
    jobs_ids = fields.One2many('nantian_erp.jobs', 'contract_id',string="合同岗位")
    money = fields.Float(string="合同金额" ,compute='_count_money',store=True)
    money_tax = fields.Float(string="税金" ,compute='_count_money_tax',store=True)
    money_total = fields.Float(string="税后总计金额" ,compute='_count_money_total',store=True)
    collection_money = fields.Float(string="收款金额", compute='_count_collection_money', store=True)
    collection_money_tax = fields.Float(string="收款税金", compute='_count_collection_money_tax', store=True)
    collection_money_total = fields.Float(string="不含税总计收款金额", compute='_count_collection_money_total', store=True)
    collection_ids = fields.One2many('nantian_erp.collection', 'contract_id',string="收款")
    detail_ids = fields.One2many('nantian_erp.detail', 'contract_id', string="维保明细")
    hr_requirements = fields.Text(string="人员要求")
    resource_requirements = fields.Text(string="资源要求")
    other = fields.Text(string="其他")
    service_content = fields.Text(string="服务内容")
    next_collection_date = fields.Date(compute='_count_next_date',string="下次收款日期",store=True)
    state = fields.Selection(
        [
            ('going', u'进行中'),
            ('renew', u'待续签'),
            ('off', u'关闭'),
        ],
        string="合同状态",default='going'
    )
    category = fields.Selection(
        [
            (u'服务合同', u'服务合同'),
            (u'维保合同', u'维保合同'),
            (u'混合合同',u'混合合同')
        ],
        string="合同类别", default=u'服务合同'
    )
    employee_ids = fields.One2many('hr.employee', 'nantian_erp_contract_id', "Employees")
    contract_ids = fields.Many2many('nantian_erp.working_team', 'working_team_to_contract',string="工作组")


    # 自动计算下次收款提醒邮件--距离收款时间一个月内 频率--每周
    @api.multi
    def email_contract_next_collection_date(self):
        subject = '您有合同即将收款，请及时处理！'
        date = fields.Date.to_string(fields.date.today()+datetime_boss.timedelta(days=30))
        user_ids = []
        for contracts in self.env['nantian_erp.contract'].search([('next_collection_date', '<=', date)]):
            if contracts.header_id not in user_ids:
                user_ids.append(contracts.header_id)
        for user_id in user_ids:
            datas = ''
            user_contracts = self.env['nantian_erp.contract'].search([('next_collection_date', '<=', date),('header_id', '=', user_id.id)])
            for user_contract in user_contracts:
                text = u'合同名:'+user_contract.name + u'-----收款时间 '+ user_contract.next_collection_date
                datas += u'<p>' + text + u'</p>'
                for collection in user_contract.collection_ids:
                    if collection.date == user_contract.next_collection_date:
                        collection_data = u'&nbsp;&nbsp;&nbsp;&nbsp;收款事项：'+collection.name+u'&nbsp;&nbsp;前提条件：'+collection.name+u'&nbsp;&nbsp;预期金额：'+ unicode(collection.evaluate_money)
                        datas += u'<p>' + collection_data + u'</p>'
            body = u'<div>' + u'<p>您好:</p>' + u'<p>&nbsp;&nbsp;&nbsp;&nbsp;以下合同即将或已经进入收款期限，请您及时处理,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a>查看详细信息</p>' + datas + u'</div>'
            self.send_email(user_id,body,subject)

    # 自动根据合同结束时间提醒邮件--距离合同结束一个月内 频率--每周
    @api.multi
    def email_contract_date_end(self):
        subject = '您有合同即将过期，请及时处理！'
        date = fields.Date.to_string(fields.date.today()+datetime_boss.timedelta(days=30))
        user_ids=[]
        for contracts in self.env['nantian_erp.contract'].search([('date_end','<=',date),('state','=','renew')]):
            if contracts.header_id not in user_ids:
                user_ids.append(contracts.header_id)
        for user_id in user_ids:
            datas=''
            user_contracts = self.env['nantian_erp.contract'].search([('date_end', '<=', date), ('state', '=', 'renew'),('header_id','=',user_id.id)])
            for user_contract in user_contracts:
                text=u'合同名:'+user_contract.name+u'-----过期时间 '+user_contract.date_end
                datas+=u'<p>'+text+u'</p>'
            body= u'<div>'+u'<p>您好:</p>'+u'<p>&nbsp;&nbsp;&nbsp;&nbsp;以下合同即将过期或已经过期，请您及时续签或关闭,您可登录：<a href="http://123.56.147.94:8000">http://123.56.147.94:8000</a>查看详细信息</p>' + datas + u'</div>'
            self.send_email(user_id,body,subject)

    #邮件发送函数
    def send_email(self, cr, uid, users, body='',subject='',context=None):
        to_list = []
        for user in users:
            to_list.append(formataddr((Header(user.name, 'utf-8').encode(), user.email)))
        mail_mail = self.pool.get('mail.mail')
        mail_id = mail_mail.create(cr, uid, {
            'body_html': body,
            'subject': subject,
            'email_to': to_list,
            'auto_delete': True,
        }, context=context)
        mail_mail.browse(cr,uid,[mail_id],context=context).email_from = '南天ERP系统<nantian_erp@nantian>'
        mail_mail.send(cr, uid, [mail_id], context=context)
    #自动检测合同结束时间>现在 --- 修改状态为待续签
    @api.multi
    def change_contract_state(self):
        for ids in self.search([('state','=','going')]):
            if ids.date_end:
                if fields.Date.from_string(ids.date_end) <= fields.date.today():
                    ids.state = 'renew'
    #合同续签功能函数
    @api.multi
    def copy_all(self):
        name = self.name+u'('+u'新续签请修改'+u')'
        new_contract=self.env['nantian_erp.contract'].create({'name': name,'header_id': self.header_id.id,'customer_id':self.customer_id.id,'date_start':self.date_start,
                                                 'date_end':self.date_end,'hr_requirements': self.hr_requirements,'resource_requirements': self.resource_requirements,
                                                 'other':self.other,'service_content':self.service_content,'state':'going','category':self.category,
                                                 })
        if self.employee_ids:
            for employee_id in self.employee_ids:
                employee_id.nantian_erp_contract_id = new_contract
        if self.collection_ids:
            for collection_id in self.collection_ids:
                new_collection = collection_id.copy()
                new_collection.contract_id = new_contract
        if self.detail_ids:
            for detail_id in self.detail_ids:
                new_detail = detail_id.copy()
                new_detail.contract_id = new_contract
        if self.jobs_ids:
            for jobs_id in  self.jobs_ids:
                new_jobs = jobs_id.copy()
                if jobs_id.employee_ids:
                    for job_hr in jobs_id.employee_ids:
                        job_hr.contract_jobs_id = new_jobs
                new_jobs.contract_id = new_contract
        self.state = 'off'
        return self.pop_window(new_contract.id)
    #续签函数页面跳转
    @api.multi
    def pop_window(self,id):
        form_id = self.env['ir.model.data'].search([('name','=','nantian_erp_contract_user'),('module','=','nantian_erp')]).res_id
        tree_id = self.env['ir.model.data'].search([('name','=','nantian_erp_contract_user_tree'),('module','=','nantian_erp')]).res_id
        value = {
            'name': ('您的合同已续签成功，请修改！'),
            'res_model': 'nantian_erp.contract',
            'views': [[tree_id,'tree'],[form_id, 'form']],
            'view_mode':'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('id','=',id)],
        }
        return value
    #合同关闭函数
    @api.multi
    def set_off(self):
        self.state = 'off'
    #对特定页面只允许创建维保合同
    @api.multi
    def onchange_category(self,name):
        result = {'value':{}}
        result['value']['category'] = u'维保合同'
        return result
    #自动计算合同需要人数
    @api.depends('jobs_ids.amount')
    def _need_count_employees(self):
        for record in self:
            record.need_employee_count = 0
            for job in record.jobs_ids:
                record.need_employee_count += job.amount
    #根据需要人数和现有人数判断是否缺员
    @api.depends('need_employee_count','employee_count')
    def _count_is_need(self):
        for record in self:
            if record.need_employee_count > record.employee_count:
                record.is_need = True
            else:
                record.is_need = False
    #计算合同现有人数
    @api.depends('employee_ids')
    def _count_employees(self):
        for record in self:
            # 加个人员有效的过滤
            liSt = []
            for employee_id in record.employee_ids:
                if employee_id.active:
                    liSt.append(employee_id)
            record.employee_count = len(liSt)

    #计算岗位现有人数
    @api.depends('jobs_ids.employee_count')
    def _count_employees_jobs(self):
        for record in self:
            for job in record.jobs_ids:
                record.employee_jobs_count += job.employee_count
    #自动计算总计金额
    @api.depends('jobs_ids.subtotal','detail_ids.subtotal','category')
    def _count_money(self):
        for record in self:
            if record.category == u'服务合同':
                for job in record.jobs_ids:
                    record.money += job.subtotal
            elif record.category == u'维保合同':
                for detail in record.detail_ids:
                    record.money += detail.subtotal
            elif record.category == u'混合合同':
                for job in record.jobs_ids:
                    record.money += job.subtotal
                for detail in record.detail_ids:
                    record.money += detail.subtotal
    #自动计算税金
    @api.depends('jobs_ids.rated_moneys','detail_ids.rated_moneys','category')
    def _count_money_tax(self):
        for record in self:
            if record.category == u'服务合同':
                for job in record.jobs_ids:
                    record.money_tax += job.rated_moneys
            elif record.category == u'维保合同':
                for detail in record.detail_ids:
                    record.money_tax += detail.rated_moneys
            elif record.category == u'混合合同':
                for job in record.jobs_ids:
                    record.money_tax += job.rated_moneys
                for detail in record.detail_ids:
                    record.money_tax += detail.rated_moneys
    #自动计算税后金额
    @api.depends('money','money_tax')
    def _count_money_total(self):
        for record in self:
            record.money_total = record.money - record.money_tax
    #自动计算下次收款日期
    @api.depends('collection_ids.date')
    def _count_next_date(self):
        for record in self:
            dates=[]
            if record.collection_ids:
                for collection in record.collection_ids:
                    if collection.state==u'未收款':
                        dates.append(collection.date)
            if dates:
                record.next_collection_date=min(dates)
            else:
                record.next_collection_date=None
    #自动计算税前金额
    @api.depends('collection_ids.money_total')
    def _count_collection_money_total(self):
        for record in self:
            for collection in record.collection_ids:
                record.collection_money_total += collection.money_total
    #自动计算收款税金
    @api.depends('collection_ids.rated_moneys')
    def _count_collection_money_tax(self):
        for record in self:
            for collection in record.collection_ids:
                record.collection_money_tax += collection.rated_moneys
    #自动计算收款金额
    @api.depends('collection_money', 'collection_money_tax')
    def _count_collection_money(self):
        for record in self:
            record.collection_money = record.collection_money_total + record.collection_money_tax
    #修改作为外键时的显示
    @api.multi
    @api.depends('name', 'employee_count')
    def name_get(self):
        return [(r.id, (r.name + '-' + u'合同约束人数' + (str(r.need_employee_count)) + u'人')) for r in self]


class res_partner(models.Model):
    _inherit = 'res.partner'

    category =fields.Selection(
        [
            (u'服务客户', u'服务客户'),
            (u'case客户', u'case客户'),
        ],

    )
    customer_manager = fields.Many2one('res.users', ondelete='set null',default=lambda self: self.env.user)
    full_name =fields.Char(string='全称')
    other_customer_managers = fields.Many2many('res.users','partner_to_user',string="其他行业负责人")
    @api.multi
    def _onchange_to_service_customer(self,name):
        value = {}
        value['category'] = u'服务客户'
        value['is_company'] = 'True'
        return {'value':value}

    @api.multi
    def _onchange_to_case_customer(self,name):
        value={}
        value['category'] = u'case客户'
        value['is_company'] = 'True'
        return {'value':value}


# 工作组
class working_team(models.Model):
    _name = 'nantian_erp.working_team'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    # _mail_post_access = 'read'
    name = fields.Char(string=u"名称")
    user_id = fields.Many2one('res.users',string=u'负责人')
    partner_id = fields.Many2one('res.partner', string=u'客户')
    employee_ids = fields.One2many('hr.employee', 'working_team_id',string=u"工作组成员")
    hr_user_ids = fields.Many2one(related='employee_ids.user_id', string=u'工作组成员用户')
    need_employee_count = fields.Integer(string=u"所需人数")
    employee_count = fields.Integer(compute='_count_employees', string=u'现有人数', store=True)
    is_need = fields.Boolean(compute='_count_is_need', string=u'缺员', store=True)
    category = fields.Selection(
        [
            (u'工作组', u'工作组'),

        ], string=u'类别', default=u'工作组'
    )
    state = fields.Selection(
        [
            (u'进行中', u'进行中'),
            (u'已关闭', u'已关闭'),
        ], string=u'状态', default=u'进行中'
    )
    contract_ids = fields.Many2many('nantian_erp.contract', 'working_team_to_contract',string="合同")

    # 根据需要人数和现有人数判断是否缺员
    @api.depends('need_employee_count', 'employee_count')
    def _count_is_need(self):
        for record in self:
            if record.need_employee_count > record.employee_count:
                record.is_need = True
            else:
                record.is_need = False
    # 在管理界面创建时默认选中类别为工作组
    # @api.multi
    # def _onchange_category(self, name):
    #     value = {}
    #     value['category'] = u'工作组'
    #     return {'value': value}

    # 自动计算工作组现有人数
    @api.depends('employee_ids')
    def _count_employees(self):
        for record in self:
            record.employee_count = len(record.employee_ids)

    # 将项目下工作组数据复制到本表---只执行一次
    # @api.multi
    # def project_export(self):
    #      projects = self.env['project.project'].search([('category', '=', '工作组')])
    #      for project in projects:
    #          work=self.create({'name':project.name,'user_id':project.user_id.id,'partner_id':project.partner_id.id,'need_employee_count':project.need_employee_count,'employee_count':project.employee_count,'category':project.category,'state':u'进行中'})
    #          work.employee_ids |= project.employee_ids

    # 自动将工作组人员及经理加入相关组
    @api.multi
    def auto_add_to_group(self):
        _logger = logging.getLogger(__name__)
        works = self.env['nantian_erp.working_team'].search([])
        work_team_user_id = self.env['ir.model.data'].search(
            [('name', '=', 'group_work_team_user'), ('module', '=', 'nantian_erp')]).res_id
        work_team_manager_id = self.env['ir.model.data'].search(
            [('name', '=', 'group_nantian_manager'), ('module', '=', 'nantian_erp')]).res_id
        group_user_id = self.env['res.groups'].search([('id', '=', work_team_user_id)])
        group_manager_id = self.env['res.groups'].search([('id', '=', work_team_manager_id)])
        for work in works:
            #_logger.info(work)
            if work.user_id not in group_manager_id.users:
                group_manager_id.users |= work.user_id
            for hr in  work.employee_ids:
                if hr.user_id not in group_user_id.users:
                    group_user_id.users |= hr.user_id


    # 修改作为外键时的显示形式
    @api.multi
    @api.depends('name', 'need_employee_count')
    def name_get(self):
        data = []
        for r  in self:
            if r.user_id:
                data.append((r.id, (r.name + '-'+r.user_id.name+'-' + u'所需人数' + (str(r.need_employee_count)) + u'人')))
            else:
                data.append((r.id, (r.name + '-' + u'所需人数' + (str(r.need_employee_count)) + u'人')))
        return data
#人员调整记录
class hr_adjusting(models.Model):
    _name = 'nantian_erp.hr_adjusting'

    def _default_SN(self):
        object = self.env['hr.employee'].browse(self._context.get('active_ids'))
        return object


    employee_id = fields.Many2many('hr.employee','emp_to_adjust_ref',string="hr",default =_default_SN,store = True)
    states = fields.Selection([
        (u'待调整', u"待调整"),
        (u'可调用', u"可调用"),
        (u'申请离职', u"申请离职"),
        (u'已离职', u"已离职"),
        (u'借调中', u"借调中"),
        (u'调整完成', u"调整完成"),
    ], default=u'待调整', string="调整状态")
    dst = fields.Char(string="调整至")
    notes = fields.Text(string=u"备注")
    adjust_date = fields.Date(string=u'可调整日期')


    @api.multi
    def subscribe(self):
        for s in self.employee_id:
            if s.dis_states ==u"待调整":
                raise exceptions.ValidationError("人员正在调整中,请取消重新处理")
                return None
            elif s.dis_states == u"申请离职":
                raise exceptions.ValidationError("人员正在离职中,请取消重新处理")
                return None
            models = self.env['hr.employee'].search([('id','=',s.id)])
            #print models.name,models.dis_states
            models.write({'dis_states':self.states})
            #print models.name,models.dis_states
        return {'aaaaaaaaaaaaaa'}


class work_experience(models.Model):
    _name = 'nantian_erp.work_experience'

    name = fields.Char()
    job = fields.Char()
    description = fields.Text()
    date = fields.Char()
    employee_id = fields.Many2one('hr.employee')


class department(models.Model):
    _inherit = 'hr.department'

    level = fields.Integer(string='级别',compute='compute_level',store=True)

    @api.multi
    @api.depends('parent_id')
    def compute_level(self):
        print '*'*80
        departments = self.env['hr.department'].search([])
        for record in departments:
            if not record.parent_id:
                record.level = 1
            elif record.parent_id.parent_id:
                record.level = 3
            else:
                record.level = 2


class education_experience(models.Model):

    _name = 'nantian_erp.education_experience'

    school =fields.Char(string='学校')
    major = fields.Char(string='专业')
    education = fields.Selection([(u'中专及以下',u'中专及以下'),(u'高中',u'高中'),(u'大专',u'大专'),(u'本科',u'本科'),(u'硕士',u'硕士'),(u'博士',u'博士')],string='学历')
    date_time = fields.Char(string='时间段')
    date_start = fields.Date(string='开始')
    date_end = fields.Date(string='结束')
    employee_id = fields.Many2one('hr.employee',string='员工')





