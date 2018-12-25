# -*- coding: utf-8 -*-
from openerp import models, api


class nt_user(models.Model):
    _inherit = 'res.users'
    
    # 修改作为外键时的显示
    @api.multi
    @api.depends('name', 'login')
    def name_get(self):
        return [(r.id, (r.name + '(' + r.login + ')')) for r in self]