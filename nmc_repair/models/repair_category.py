# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _


class RepairCategory(models.Model):
  _name='repair.category'
  _description = 'Repair Category'
  name = fields.Char(translate=True)
  