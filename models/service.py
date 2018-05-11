# -*- coding: utf-8 -*-
from openerp import tools
from openerp import models, fields, api,exceptions
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class service_type(models.Model):
    _name = "nantian_erp.service"

    type = fields.Char(string="业务类型")
    partner_id = fields.Many2one('res.partner', string="客户")
    user_id = fields.Many2one('res.users', string="业务负责人")
    sale_user_id = fields.Many2one('res.users', string="销售负责人")
