# -*- coding: utf-8 -*-

from odoo import api, fields, models
import pytz
from datetime import datetime


class accountMoveLine(models.Model):
    _inherit = 'account.move.line'
    date = fields.Date(readonly=False, related='move_id.date')
