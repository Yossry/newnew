from odoo import models, fields, api
import datetime

class EventType(models.Model):
    _inherit = "event.type"
    in_house = fields.Boolean()
    study_format = fields.Selection(
    	[('multiple','Multiple Formats'),('live','Live Class'),('liveonline','Live Online'),('self','Self-Study'),('online','Online'),('inhouse','In House'),('private','Private Tutoring')],
    	string='Study Format',
    	required="1")
    
    event_type_mail_ids = fields.One2many(
        'event.type.mail', 'event_type_id', string='Communication Schedule',
        copy=False,
        default=lambda self: self._get_default_event_type_mail_ids())

    auto_confirm = fields.Boolean(default=False)
        
    @api.model
    def _get_default_event_type_mail_ids(self):
        return [(0, 0, {
	        'notification_type': 'mail',
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref('event.event_subscription').id,
        }), (0, 0, {
	        'notification_type': 'mail',
            'interval_nbr': 1,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('event.event_reminder').id,
        }), (0, 0, {
	        'notification_type': 'mail',
            'interval_nbr': 10,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('event.event_reminder').id,
        })]