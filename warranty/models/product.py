# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_warranty = fields.Boolean(string='Has Warranty')
