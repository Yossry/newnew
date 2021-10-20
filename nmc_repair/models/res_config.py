# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jc_contact = fields.Text(string="Service Center Contact", translate=True)
    jc_opening_hours = fields.Text(string="Service Center opening hours", translate=True)
    jc_tc = fields.Html(string="Service Center Terms & Conditions", translate=True)

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param(
            "nmc_repair.jc_contact", self.jc_contact
        )
        IrConfigPrmtr.set_param(
            "nmc_repair.jc_opening_hours", self.jc_opening_hours
        )
        IrConfigPrmtr.set_param(
            "nmc_repair.jc_tc", self.jc_tc
        )


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        res.update({
            'jc_contact' : IrConfigPrmtr.get_param('nmc_repair.jc_contact'),
            'jc_opening_hours' : IrConfigPrmtr.get_param('nmc_repair.jc_opening_hours'),
            'jc_tc' : IrConfigPrmtr.get_param('nmc_repair.jc_tc'),
        })
        return res