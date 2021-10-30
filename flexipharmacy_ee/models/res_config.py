# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # birthday reminder
    enable_birthday_reminder = fields.Boolean(string="Birthday Reminder")
    birthday_template_id = fields.Many2one('mail.template', string="Birthday Mail Template")
    # Auto Close POS all session
    enable_auto_close_session = fields.Boolean(string="Automatic Close Session")
    # Anniversary reminder
    enable_anniversary_reminder = fields.Boolean(string="Anniversary Reminder")
    anniversary_template_id = fields.Many2one('mail.template', string="Anniversary Template")
    # generate Barcode
    gen_barcode = fields.Boolean("On Product Create Generate Barcode")
    barcode_selection = fields.Selection([('code_39', 'CODE 39'), ('code_128', 'CODE 128'),
                                          ('ean_13', 'EAN-13'), ('ean_8', 'EAN-8'),
                                          ('isbn_13', 'ISBN 13'), ('isbn_10', 'ISBN 10'),
                                          ('issn', 'ISSN'), ('upca', 'UPC-A')], string="Select Barcode Type")
    gen_internal_ref = fields.Boolean(string="On Product Create Generate Internal Reference")
    # product Expiry report
    mailsend_check = fields.Boolean(string="Send Mail")
    email_notification_days = fields.Integer(string="Expiry Alert Days")
    res_user_ids = fields.Many2many('res.users', string='Users')
    # Doctor commision
    pos_commission_calculation = fields.Selection([
        ('product', 'Product'),
        ('product_category', 'Product Category'),
        ('doctor', 'Doctor'),
    ], string='Commission Calculation ')
    pos_account_id = fields.Many2one('account.account', string='Commission Account ')
    pos_commission_based_on = fields.Selection([
        ('product_sell_price', 'Product Sell Price'),
        ('product_profit_margin', 'Product Profit Margin')
    ], string='Commission Based On ')
    pos_commission_with = fields.Selection([
        ('with_tax', 'Tax Included'),
        ('without_tax', 'Tax Excluded')
    ], string='Apply Commission With ')
    is_doctor_commission = fields.Boolean(string='Doctor Commission ')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter'].sudo()
        res_user_ids = param_obj.sudo().get_param('flexipharmacy_ee.res_user_ids')
        if res_user_ids:
            res.update({
                'res_user_ids': literal_eval(res_user_ids),
            })
        res.update({
            'mailsend_check': self.env['ir.config_parameter'].sudo().get_param('flexipharmacy_ee.mailsend_check'),
            'email_notification_days': int(param_obj.sudo().get_param('flexipharmacy_ee.email_notification_days')),
            'enable_birthday_reminder': param_obj.get_param('flexipharmacy_ee.enable_birthday_reminder'),
            'birthday_template_id': int(param_obj.get_param('flexipharmacy_ee.birthday_template_id')),
            'enable_anniversary_reminder': param_obj.get_param('flexipharmacy_ee.enable_anniversary_reminder'),
            'anniversary_template_id': int(param_obj.get_param('flexipharmacy_ee.anniversary_template_id')),
            'enable_auto_close_session': param_obj.get_param('flexipharmacy_ee.enable_auto_close_session'),

            'gen_barcode': param_obj.get_param('gen_barcode'),
            'barcode_selection': param_obj.get_param('barcode_selection'),
            'gen_internal_ref': param_obj.get_param('gen_internal_ref'),
            'pos_commission_calculation': param_obj.get_param('flexipharmacy_ee.pos_commission_calculation'),
            'pos_commission_based_on': param_obj.get_param('flexipharmacy_ee.pos_commission_based_on'),
            'pos_commission_with': param_obj.get_param('flexipharmacy_ee.pos_commission_with'),
            'is_doctor_commission': param_obj.get_param('flexipharmacy_ee.is_doctor_commission'),
        })
        IrDefault = self.env['ir.default'].sudo()
        pos_account_id = IrDefault.get('res.config.settings', "pos_account_id")
        res.update({'pos_account_id': pos_account_id or False})
        return res

    def set_values(self):
        param_obj = self.env['ir.config_parameter'].sudo()
        param_obj.sudo().set_param('flexipharmacy_ee.enable_birthday_reminder', self.enable_birthday_reminder)
        param_obj.sudo().set_param('flexipharmacy_ee.birthday_template_id', self.birthday_template_id.id)
        param_obj.sudo().set_param('flexipharmacy_ee.enable_anniversary_reminder', self.enable_anniversary_reminder)
        param_obj.sudo().set_param('flexipharmacy_ee.anniversary_template_id', self.anniversary_template_id.id)
        param_obj.sudo().set_param('flexipharmacy_ee.enable_auto_close_session', self.enable_auto_close_session)

        param_obj.sudo().set_param('gen_barcode', self.gen_barcode)
        param_obj.sudo().set_param('barcode_selection', self.barcode_selection)
        param_obj.sudo().set_param('gen_internal_ref', self.gen_internal_ref)
        param_obj.sudo().set_param("flexipharmacy_ee.pos_commission_calculation", self.pos_commission_calculation)
        param_obj.sudo().set_param("flexipharmacy_ee.pos_commission_based_on", self.pos_commission_based_on)
        param_obj.sudo().set_param("flexipharmacy_ee.pos_commission_with", self.pos_commission_with)
        param_obj.sudo().set_param("flexipharmacy_ee.is_doctor_commission", self.is_doctor_commission)
        param_obj.sudo().set_param('flexipharmacy_ee.mailsend_check', self.mailsend_check)
        param_obj.sudo().set_param('flexipharmacy_ee.res_user_ids', self.res_user_ids.ids)
        param_obj.sudo().set_param('flexipharmacy_ee.email_notification_days', self.email_notification_days)
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', "pos_account_id", self.pos_account_id.id)
        return super(ResConfigSettings, self).set_values()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
