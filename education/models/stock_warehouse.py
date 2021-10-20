from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"
    company_id = fields.Many2one('res.company')
    name = fields.Char('Warehouse Name')
    partner_id = fields.Many2one('res.partner',string="Address")