# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
