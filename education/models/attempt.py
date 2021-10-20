from odoo import models, fields, api
from odoo.exceptions import UserError


class Attempt(models.Model):
    _name = 'attempt'
    _description = 'Attempt'
    name = fields.Char('Attempt', compute='_compute_Attempt_number')
    student_id = fields.Many2one('res.partner', string="Student")
    event_id = fields.Many2one('event.event', string="Event")
    course_id = fields.Many2one('course', string="Course")
    attempt_date = fields.Date('Attempt Date')
    passing_status = fields.Selection(
        [
            ('passed', 'Passed'),
            ('failed', 'Failed')
        ],
        string='Passing Status')
    score = fields.Float('Score')
    registration_id = fields.Many2one('event.registration')
    product_registration_id = fields.Many2one('product.registration')

    order_id = fields.Many2one('sale.order', 'Order')
    sale_order_line = fields.Many2one('sale.order.line', 'Sale order line')
    is_self_study = fields.Boolean(string='Is self study')

    def _compute_Attempt_number(self):
        for record in self:
            registration = self.env['event.registration'].browse(record.student_id.id)
            count = len(registration.attempt_ids)
            record['name'] = str(++count)

    @api.model
    def create(self, vals):
        record = super(Attempt, self).create(vals)
        if self.sale_order_line:
            if self.sale_order_line.event_id:
                record['event_id'] = self.sale_order_line.event_id.id

            else:
                record['is_self_study'] = True

        return record
