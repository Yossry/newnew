# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SessionConfigurator(models.TransientModel):
    _name = 'event.track.configurator'
    _description = 'Session Configurator'
    
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    event_id = fields.Many2one('event.event', string="Event")
    session_id = fields.Many2one('event.track', string="Session")