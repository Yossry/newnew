from odoo import models, fields


class Package(models.Model):
    _inherit = 'stock.quant.package'
    tax_id = fields.Many2one('account.tax', string='Tax')
    name = fields.Char('Name')
    price = fields.Float('Price')
    cost = fields.Float('Cost')
    package_type = fields.Selection(
        [
            ('standalone', 'Standalone'),
            ('package', 'Package'),
            ('add on', 'Add On')
        ],
        string='Type', readonly='trues')
