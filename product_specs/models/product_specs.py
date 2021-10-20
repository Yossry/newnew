# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests



class ProductSpecs(models.Model):
  _name='product.specs'
  _description='Product Specs'
  name=fields.Char(string='Title',translate=True)
  description=fields.Text(string='Description',translate=True)
  product_id = fields.Many2one('product.product',string='Product')
  

    