# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Parter_Inherit(models.Model):
    _inherit = "res.partner"

    pre = fields.Many2one("account.son",string=u'预付账款')
    rec = fields.Many2one("account.son",string=u'应付账款')
    group = fields.Selection([
        ('in','内关联'),
        ('out','外关联'),
        ('none','非关联')
    ],string=u'集团分类')

class account_son(models.Model):
    _name = "account.son"

    code_num = fields.Char(string=u'代号')
    name = fields.Char(string=u'名称',default='New')
    clas = fields.Char(string=u'分类')

