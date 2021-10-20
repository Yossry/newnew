# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests



class Product(models.Model):
  _inherit='product.product'
  spec_ids=fields.One2many('product.specs','product_id',string='Specs')
  

  	



    