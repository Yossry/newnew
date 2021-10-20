from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, MissingError
from dateutil.relativedelta import relativedelta
from babel.dates import format_datetime, format_date
from odoo.tools import float_compare, float_is_zero


class SessionRegistration(models.Model):
    _name = 'session.registration'
    _description = 'Session Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name, create_date desc'

    # session
    origin = fields.Char(
        string='Source Document', readonly=True,
        help="Reference of the document that created the registration, for example a sales order")
    session_id = fields.Many2one(
        'event.track', string='Session', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    # attendee
    partner_id = fields.Many2one(
        'res.partner', string='Contact',
        states={'done': [('readonly', True)]})
    name = fields.Char(string='Attendee Name', index=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    # organization
    date_open = fields.Datetime(string='Registration Date', readonly=True,
                                default=lambda self: fields.Datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(string='Attended Date', readonly=True)
    session_date = fields.Datetime(string="Session Date", related='session_id.date', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='session_id.event_id.company_id',
        store=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('open', 'Confirmed'), ('done', 'Attended')],
        string='Status', default='draft', readonly=True, copy=False, tracking=True)

    @api.constrains('session_id', 'state')
    def _check_seats_limit(self):
        for registration in self:
            if registration.session_id.event_id.seats_availability == 'limited' and registration.session_id.event_id.seats_max and registration.session_id.event_id.seats_available < (
                    1 if registration.state == 'draft' else 0):
                raise ValidationError(_('No more seats available for this session.'))

    @api.model
    def create(self, vals):
        registration = super(SessionRegistration, self).create(vals)
        registration.sudo().confirm_registration()
        return registration

    @api.model
    def _prepare_attendee_values(self, registration):
        """ Method preparing the values to create new attendees based on a
        sales order line. It takes some registration data (dict-based) that are
        optional values coming from an external input like a web page. This method
        is meant to be inherited in various addons that sell events. """
        partner_id = registration.pop('partner_id', self.env.user.partner_id)
        session_id = registration.pop('session_id', False)
        data = {
            'name': registration.get('name', partner_id.name),
            'phone': registration.get('phone', partner_id.phone),
            'mobile': registration.get('mobile', partner_id.mobile),
            'email': registration.get('email', partner_id.email),
            'partner_id': partner_id.id,
            'session_id': session_id and session_id.id or False,
        }
        data.update({key: value for key, value in registration.items() if key in self._fields})
        return data

    def do_draft(self):
        self.write({'state': 'draft'})

    def confirm_registration(self):
        self.write({'state': 'open'})

    def button_reg_close(self):
        """ Close Registration """
        for registration in self:
            today = fields.Datetime.now()
            if registration.session_id.event_id.date_begin <= today and registration.session_id.event_id.state == 'confirm':
                registration.write({'state': 'done', 'date_closed': today})
            elif registration.session_id.state == 'draft':
                raise UserError(_("You must wait the event confirmation before doing this action."))
            else:
                raise UserError(_("You must wait the event starting day before doing this action."))

    def button_reg_cancel(self):
        self.write({'state': 'cancel'})

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            contact_id = self.partner_id.address_get().get('contact', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                self.name = contact.name or self.name
                self.email = contact.email or self.email
                self.phone = contact.phone or self.phone
                self.mobile = contact.mobile or self.mobile

    def _message_get_suggested_recipients(self):
        recipients = super(SessionRegistration, self)._message_get_suggested_recipients()
        public_users = self.env['res.users'].sudo()
        public_groups = self.env.ref("base.group_public", raise_if_not_found=False)
        if public_groups:
            public_users = public_groups.sudo().with_context(active_test=False).mapped("users")
        try:
            for attendee in self:
                is_public = attendee.sudo().with_context(
                    active_test=False).partner_id.user_ids in public_users if public_users else False
                if attendee.partner_id and not is_public:
                    attendee._message_add_suggested_recipient(recipients, partner=attendee.partner_id,
                                                              reason=_('Customer'))
                elif attendee.email:
                    attendee._message_add_suggested_recipient(recipients, email=attendee.email,
                                                              reason=_('Customer Email'))
        except AccessError:  # no read access rights -> ignore suggested recipients
            pass
        return recipients

    def _message_get_default_recipients(self):
        # Prioritize registration email over partner_id, which may be shared when a single
        # partner booked multiple seats
        return {r.id: {
            'partner_ids': [],
            'email_to': r.email,
            'email_cc': False}
            for r in self}

    def _message_post_after_hook(self, message, msg_vals):
        if self.email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email', '=', new_partner.email),
                    ('state', 'not in', ['cancel']),
                ]).write({'partner_id': new_partner.id})
        return super(SessionRegistration, self)._message_post_after_hook(message, msg_vals)

    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'event_badge'
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('event.event_registration_mail_template_badge')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='session.registration',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_light",
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def get_date_range_str(self):
        self.ensure_one()
        today = fields.Datetime.now()
        event_date = self.event_begin_date
        diff = (event_date.date() - today.date())
        if diff.days <= 0:
            return _('today')
        elif diff.days == 1:
            return _('tomorrow')
        elif (diff.days < 7):
            return _('in %d days') % (diff.days,)
        elif (diff.days < 14):
            return _('next week')
        elif event_date.month == (today + relativedelta(months=+1)).month:
            return _('next month')
        else:
            return _('on ') + format_datetime(self.env, self.session_id.date, tz=self.session_id.event_id.date_tz,
                                              dt_format='medium')

    def summary(self):
        self.ensure_one()
        return {'information': []}

        # in addition to origin generic fields, add real relational fields to correctly

    # handle attendees linked to sales orders and their lines
    # TDE FIXME: maybe add an onchange on sale_order_id + origin
    sale_order_id = fields.Many2one('sale.order', string='Source Sales Order', ondelete='cascade')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sales Order Line', ondelete='cascade')
    campaign_id = fields.Many2one('utm.campaign', 'Campaign', related="sale_order_id.campaign_id", store=True)
    source_id = fields.Many2one('utm.source', 'Source', related="sale_order_id.source_id", store=True)
    medium_id = fields.Many2one('utm.medium', 'Medium', related="sale_order_id.medium_id", store=True)

    @api.constrains('session_id', 'state')
    def _check_ticket_seats_limit(self):
        for record in self:
            if record.session_id.event_id.seats_max and record.session_id.event_id.seats_available < 0:
                raise ValidationError(_('No more available seats for this session'))

    def _check_auto_confirmation(self):
        res = super(SessionRegistration, self)._check_auto_confirmation()
        if res:
            orders = self.env['sale.order'].search(
                [('state', '=', 'draft'), ('id', 'in', self.mapped('sale_order_id').ids)], limit=1)
            if orders:
                res = False
        return res

    @api.model
    def create(self, vals):
        res = super(SessionRegistration, self).create(vals)
        if res.origin or res.sale_order_id:
            res.message_post_with_view('mail.message_origin_link',
                                       values={'self': res, 'origin': res.sale_order_id},
                                       subtype_id=self.env.ref('mail.mt_note').id)
        return res

    @api.model
    def _prepare_attendee_values(self, registration):
        """ Override to add sale related stuff """
        line_id = registration.get('sale_order_line_id')
        if line_id:
            registration.setdefault('partner_id', line_id.order_id.partner_id)
        att_data = super(SessionRegistration, self)._prepare_attendee_values(registration)
        if line_id:
            att_data.update({
                'session_id': line_id.session_id.id,
                'session_id': line_id.session_id.id,
                'origin': line_id.order_id.name,
                'sale_order_id': line_id.order_id.id,
                'sale_order_line_id': line_id.id,
            })
        return att_data

    def summary(self):
        res = super(SessionRegistration, self).summary()
        information = res.setdefault('information', {})
        information.append((_('Name'), self.name))
        order = self.sale_order_id.sudo()
        order_line = self.sale_order_line_id.sudo()
        if not order or float_is_zero(order_line.price_total, precision_digits=order.currency_id.rounding):
            payment_status = _('Free')
        elif not order.invoice_ids or any(invoice.state != 'paid' for invoice in order.invoice_ids):
            payment_status = _('To pay')
            res['alert'] = _('The registration must be paid')
        else:
            payment_status = _('Paid')
        information.append((_('Payment'), payment_status))
        return res
