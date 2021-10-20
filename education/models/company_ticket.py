from odoo import models, fields

class CompanyTicket(models.Model):
    _name = 'course.ticket.price'
    _description = 'Course Ticket Price'
    name = fields.Char('Name')
    product_id = fields.Many2one('Product.product', string="Product")
    deadline = fields.Date('Sales End')
    price = fields.Float('Price')
    ticket_ids = fields.One2many('company.price', 'ticket_id')
      