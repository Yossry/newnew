# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

from odoo.exceptions import ValidationError
import datetime
from datetime import timedelta
from dateutil import parser


class Account(models.Model):
    _inherit = 'account.account'
    old_id = fields.Integer()
    

    