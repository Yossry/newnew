# -*- coding: utf-8 -*-

import datetime
from odoo import models, api, _, _lt, fields

class AccountGeneralLedger(models.AbstractModel):
  _inherit='account.general.ledger'


  @api.model
  def _force_strict_range(self, options):
    new_options = options.copy()
    new_options['date'] = new_options['date'].copy()
    new_options['date']['strict_range'] = True
    return new_options
