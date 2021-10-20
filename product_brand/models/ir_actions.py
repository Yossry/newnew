# -*- coding: utf-8 -*-

import odoo
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import MissingError, UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval, test_python_expr
from odoo.tools import pycompat, wrap_module
from odoo.http import request

import base64
from collections import defaultdict
import datetime
import logging
import time


from pytz import timezone

_logger = logging.getLogger(__name__)



class Actions(models.Model):
  _inherit='ir.actions.actions'


  @api.model
  @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'model_name')
  def get_bindings(self, model_name):
  	cr = self.env.cr
  	query = """ SELECT a.id, a.type, a.binding_type FROM ir_actions a, ir_model m WHERE a.binding_model_id=m.id AND m.model=%s ORDER BY a.id """
  	cr.execute(query, [model_name])
  	result = defaultdict(list)
  	user_groups = self.env.user.groups_id
  	for action_id, action_model, binding_type in cr.fetchall():
  		try:
  			if(self.env[action_model]):
  				action = self.env[action_model].browse(action_id)
  				action_groups = getattr(action, 'groups_id', ())
  				if action_groups and not action_groups & user_groups:
  					continue
  				result[binding_type].append(action.read()[0])
  		except (AccessError, MissingError):
  			continue
  	return result



    