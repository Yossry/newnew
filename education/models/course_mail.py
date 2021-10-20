from odoo import models, fields, _, api


class CourseMail(models.Model):
    _name = 'course.mail'
    _description = 'Mail Scheduling on Course'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin']
    sequence = fields.Integer('Priority')
    course_id = fields.Many2one(
        'course', string='Course',
        ondelete='cascade', required=True)
    notification_type = fields.Selection([('mail', 'Mail'), ('sms', 'SMS')], string='Send', default='mail', required=True)
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hours'), ('days', 'Days'),
        ('weeks', 'Weeks'), ('months', 'Months')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_sub', 'After each registration'),
        ('before_event', 'Before the event'),
        ('after_event', 'After the event')],
        string='Trigger', default="before_event", required=True)
    template_id = fields.Many2one(
        'mail.template', string='Email Template',
        domain=[('model', '=', 'event.registration')], ondelete='restrict',
        help='This field contains the template of the mail that will be automatically sent')
    sms_template_id = fields.Many2one(
        'sms.template', string='SMS Template',
        domain=[('model', '=', 'event.registration')], ondelete='restrict',
        help='This field contains the template of the SMS that will be automatically sent')