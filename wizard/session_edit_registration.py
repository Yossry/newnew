# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class RegistrationEditor(models.TransientModel):
    _inherit = "registration.editor"
    _description = 'Edit Attendee Details on Sales Confirmation'
    sale_order_id = fields.Many2one('sale.order', 'Sales Order', required=True)
    session_registration_ids = fields.One2many('registration.editor.line', 'editor_id', string='Registrations to Edit')

    @api.model
    def default_get(self, fields):
        res = super(RegistrationEditor, self).default_get(fields)
        if not res.get('sale_order_id'):
            sale_order_id = res.get('sale_order_id', self._context.get('active_id'))
            res['sale_order_id'] = sale_order_id
        sale_order = self.env['sale.order'].browse(res.get('sale_order_id'))

        partner = sale_order.partner_id
        name = email = phone = mobile = False
        if partner.account_type == 'b2c':
            name = partner.name
            email = partner.email
            phone = partner.phone
            mobile = partner.mobile

        event_registrations = self.env['event.registration'].search([
            ('sale_order_id', '=', sale_order.id),
            ('event_id', 'in', sale_order.mapped('order_line.event_id').ids),
            ('state', '!=', 'cancel')])
        event_attendee_list = []
        for so_line in [l for l in sale_order.order_line if l.event_id]:
            existing_registrations = [r for r in event_registrations if r.event_id == so_line.event_id]
            #raise UserError(existing_registrations)
            for reg in existing_registrations:
                event_attendee_list.append({
                    'event_id': reg.event_id.id,
                    'registration_id': reg.id,
                    'name': reg.name or name,
                    'email': reg.email or email,
                    'phone': reg.phone or phone,
                    'mobile': reg.mobile or mobile,
                    'sale_order_line_id': so_line.id,
                })
            for count in range(int(so_line.product_uom_qty) - len(existing_registrations)):
                event_attendee_list.append([0, 0, {
                    'event_id': so_line.event_id.id,
                    'event_ticket_id': so_line.event_ticket_id.id,
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'mobile': mobile,
                    'sale_order_line_id': so_line.id,
                }])
        #raise UserError(str(attendee_list))
        res['event_registration_ids'] = event_attendee_list


        session_registrations = self.env['event.registration'].search([
            ('sale_order_id', '=', sale_order.id),
            ('session_id', 'in', sale_order.mapped('order_line.session_id').ids),
            ('state', '!=', 'cancel')])


        session_attendee_list = []
        for so_line in [l for l in sale_order.order_line if l.session_id]:
            existing_registrations = [r for r in session_registrations if r.session_id == so_line.session_id]
            #raise UserError(existing_registrations)
            for reg in existing_registrations:
                session_attendee_list.append({
                    'session_id': reg.session_id.id,
                    'registration_id': reg.id,
                    'name': reg.name or name,
                    'email': reg.email or email,
                    'phone': reg.phone or phone,
                    'mobile': reg.mobile or mobile,
                    'sale_order_line_id': so_line.id,
                })
            for count in range(int(so_line.product_uom_qty) - len(existing_registrations)):
                session_attendee_list.append([0, 0, {
                    'session_id': so_line.session_id.id,
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'mobile': mobile,
                    'sale_order_line_id': so_line.id,
                }])
        #raise UserError(str(attendee_list))
        res['session_registration_ids'] = session_attendee_list


        res = self._convert_to_write(res)
        return res

    def action_make_registration(self):
        self.ensure_one()

        for event_registration in self.event_registration_ids:
            event_values = event_registration.get_event_registration_data()
            #raise UserError(str(event_values))
            if event_registration.registration_id:
                event_registration.registration_id.write(event_values)

            else:
                event_regist = self.env['event.registration'].create(event_values)
                event_regist.do_draft()



        for registration_line in self.session_registration_ids:
            session_values = registration_line.get_registration_data()
            if registration_line.registration_id:
                registration_line.registration_id.write(session_values)
            else:
                session_regist = self.env['event.registration'].create(session_values)
                session_regist.do_draft()

        self.sale_order_id.action_confirm_order()

        #raise UserError(self.sale_order_id)

        ##if self.env.context.get('active_model') == 'sale.order':
            ##for order in self.env['sale.order'].browse(self.env.context.get('active_ids', [])):
                ##order.order_line._update_registrations(confirm=False)


            ##self.env['sale.order'].browse(self.env.context.get('active_ids', []))._action_confirm()

        return {'type': 'ir.actions.act_window_close'}


class RegistrationEditorLine(models.TransientModel):
    """Event Registration"""
    _inherit = "registration.editor.line"
    _description = 'Edit Attendee Line on Sales Confirmation'

    editor_id = fields.Many2one('registration.editor')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sales Order Line')
    session_id = fields.Many2one('event.track', string='Session', required=False)
    registration_id = fields.Many2one('event.registration', 'Original Registration')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    name = fields.Char(string='Name', index=True)

    def get_event_registration_data(self):
        self.ensure_one()
        return {
            'event_id': self.event_id.id,
            'partner_id': self.editor_id.sale_order_id.partner_id.id,
            'name': self.name or self.editor_id.sale_order_id.partner_id.name,
            'phone': self.phone or self.editor_id.sale_order_id.partner_id.phone,
            'mobile': self.mobile or self.editor_id.sale_order_id.partner_id.mobile,
            'email': self.email or self.editor_id.sale_order_id.partner_id.email,
            'origin': self.editor_id.sale_order_id.name,
            'sale_order_id': self.editor_id.sale_order_id.id,
            'sale_order_line_id': self.sale_order_line_id.id,
            'state': 'draft'
        }


    def get_registration_data(self):
        self.ensure_one()
        return {
            'session_id': self.session_id.id,
            'partner_id': self.editor_id.sale_order_id.partner_id.id,
            'name': self.name or self.editor_id.sale_order_id.partner_id.name,
            'phone': self.phone or self.editor_id.sale_order_id.partner_id.phone,
            'mobile': self.mobile or self.editor_id.sale_order_id.partner_id.mobile,
            'email': self.email or self.editor_id.sale_order_id.partner_id.email,
            'origin': self.editor_id.sale_order_id.name,
            'sale_order_id': self.editor_id.sale_order_id.id,
            'sale_order_line_id': self.sale_order_line_id.id,
            'state': 'draft'
        }
