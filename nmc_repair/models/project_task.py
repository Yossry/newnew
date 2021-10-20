# -*- coding: utf-8 -*-
import logging
from ast import literal_eval
import datetime
from dateutil import parser
from odoo import api, fields, models, _
import json
import requests
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class Task(models.Model):
    _inherit = 'project.task'
    condition = fields.Text('Condition')
    issue = fields.Text('Issue')
    bought_from = fields.Datetime('Bought From')
    received_images = fields.Many2many('ir.attachment', string="Images")
    categ_id = fields.Many2one('repair.category', string="Category")

    def get_opening_hours(self):
        return self.env['ir.config_parameter'].sudo().get_param('nmc_repair.jc_opening_hours', default=True)

    def get_jc_contact_number(self):
        return self.env['ir.config_parameter'].sudo().get_param('nmc_repair.jc_contact', default=True)

    def get_terms_conditions(self):
        return self.env['ir.config_parameter'].sudo().get_param('nmc_repair.jc_tc', default=True)
