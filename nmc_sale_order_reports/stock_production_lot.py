# -*- coding: utf-8 -*-

from odoo import api, fields
from odoo.exceptions import UserError


class Serial(models.Model):
    _inherit = 'stock.production.lot'


    def fix_serials(self):
    	raise Warning('test')
