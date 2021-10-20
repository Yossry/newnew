from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    currency_id = fields.Many2one('res.currency', string="Currency")
    comment = fields.Char('Comment')
    region_id = fields.Many2one('res.company', string="Region")
    date_planned = fields.Date('Scheduled Date')
    is_region = fields.Boolean('Is Region')
    stage = fields.Selection(
        [('pending', 'Pending'),
        ('approved', 'Approved By Operartion'),
        ('cfo', 'CFO'),
        ('rejected', 'Rejected By Operation'),
        ('accountingapproved', 'Approved By accounting'),
        ('accountingreject', 'Rejected By Accounting')],
        string='Decision Maker')
    is_operation = fields.Boolean('Is Operation')
    timesheet_id = fields.Many2one('res.partner')
    name = fields.Char('Reference')
    order_date = fields.Date('Date Order')
    reason_for_rejection = fields.Text('Reason For Rejection')
    instructor_timesheets = fields.One2many('purchase.order', 'timesheet_id')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    def submit_order(self):
        self.ensure_one()
        self.write({'state': 'pendingbm'})
