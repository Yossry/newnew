# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests
from odoo.exceptions import UserError


class ProductWarrantyType(models.Model):
    _name = 'product.warranty.type'

    name = fields.Char(string='Name', store=False, compute='_compute_name')
    years = fields.Char(string='Year(s)', required=True)
    type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], string='Type', default='fixed')
    value = fields.Float(string='Value', required=True)
    variant_id = fields.Many2one('product.attribute.value', string='Variant', required=True)
    number_of_days = fields.Integer(string='Number Of Days')
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, required=True)

    @api.model
    def create(self, vals):
        warranty_type = super(ProductWarrantyType, self).create(vals)
        value = False
        if (warranty_type.type == 'fixed'):
            value = warranty_type.value
            attribute_values = self.env['product.template.attribute.value'].search(
                [('product_attribute_value_id', '=', warranty_type.variant_id.id)])
            for attribute_value in attribute_values:
                attribute_values.write({'price_extra': value})

        elif (warranty_type.type == 'percentage'):
            attribute_values = self.env['product.template.attribute.value'].search(
                [('product_attribute_value_id', '=', warranty_type.variant_id.id)])
            for attribute_value in attribute_values:
                price = attribute_value.product_tmpl_id.list_price
                percentage = warranty_type.value
                value = (percentage * price) / 100
                attribute_value.write({'price_extra': value})

        return warranty_type

    def write(self, vals):
        res = super(ProductWarrantyType, self).write(vals)
        for warranty_type in self:
            value = False
            if (warranty_type.type == 'fixed'):
                value = warranty_type.value
                attribute_values = self.env['product.template.attribute.value'].search(
                    [('product_attribute_value_id', '=', warranty_type.variant_id.id)])
                for attribute_value in attribute_values:
                    attribute_values.write({'price_extra': value})

            elif (warranty_type.type == 'percentage'):
                attribute_values = self.env['product.template.attribute.value'].search(
                    [('product_attribute_value_id', '=', warranty_type.variant_id.id)])
                for attribute_value in attribute_values:
                    price = attribute_value.product_tmpl_id.list_price
                    percentage = warranty_type.value
                    value = (percentage * price) / 100
                    attribute_value.write({'price_extra': value})

        return res

    @api.onchange('type')
    def _onchange_type(self):
        self.value = 0

    def _compute_name(self):
        for record in self:
            price_label = ''
            if (record.type == 'percentage'):
                price_label = '%'

            else:
                price_label = record.currency_id.name

            record.name = record.years + ' - ' + str(record.value) + ' ' + price_label
