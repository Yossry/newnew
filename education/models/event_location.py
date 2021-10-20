from odoo import models, fields, api


class EventLocation(models.Model):
    _inherit = 'event.track.location'
    name = fields.Char('Title')
    region_id = fields.Many2one('res.company', string="Region")
    capacity = fields.Integer('Class Capacity')
    on_premises = fields.Boolean('On Premises')
    street = fields.Char(string="Address")
    street2 = fields.Char(string='Street2', translate=True)
    longtitude = fields.Char('Longtitude')
    latitude = fields.Char('Latitude')
    class_conflict = fields.Boolean(string='Has Capacity Conflict',
                                    compute='_compute_class_conflict')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State')
    city = fields.Char(string='City', translate=True)
    zip_id = fields.Char(string='Zip', translate=True)
    location_id = fields.Many2one('res.partner', 'Location')
    
    def _compute_class_conflict(self):
        for record in self:
            record.class_conflict = False
                
    @api.onchange('on_premises')
    def _onchange_on_premises(self):
        val = {}
        location = False
        if(self.region_id):
            location = self.region_id.partner_id.id
        val['value'] = {
        	'location_id': location
        }
        return val