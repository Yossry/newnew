# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseComment(models.TransientModel):
    _name = "purchase.comment.wizard"
    name = fields.Char('Name')
    stage = fields.Selection([('pending','pending'),('approved','Approved By Operation'),('rejected','Rejected By Operation'),('accountingapproved','Approved By Accounting'),('accountingreject','Rejected By Accounting')])
    type = fields.Selection([('approve', 'Approve'),('return', 'Return'),('reject', 'Reject')])
    purchase_id = fields.Many2one('purchase.order','Purchase')
    comment = fields.Text('Comment')

    def validate_comment(self):
        self.ensure_one()
        purchase = self.purchase_id
        template = self.env.ref('education.purchase_email_template')
        template.write({'email_to': False})
        if(self.type=='approve' and purchase.state == 'pendingbm'):
            group = self.env['res.groups'].browse(self.env.ref('education.country_management').id)
            for user in group.users:
                if(template.email_to):
                    template.write({'email_to': template.email_to + user.email + ','})
                else:
                    template.write({'email_to': user.email + ','})

            template.write({'body_html': self.comment})
            template.send_mail(purchase.id,force_send=True)
            purchase.write({'state': 'pendingcm'})

        elif(self.type=='approve' and purchase.state == 'pendingcm'):
            group = self.env['res.groups'].browse(self.env.ref('education.accounting_management').id)
            for user in group.users:
                if(template.email_to):
                    template.write({'email_to': template.email_to + user.email + ','})
                else:
                    template.write({'email_to': user.email + ','})

                template.write({'body_html': self.comment})

            template.send_mail(purchase.id,force_send=True)
            purchase.write({'state': 'pendingacc'})

        elif(self.type=='approve' and purchase.state == 'pendingacc'):
            group = self.env['res.groups'].browse(self.env.ref('education.pos_group').id)
            for user in group.users:
                if(template.email_to):
                    template.write({'email_to': template.email_to + user.email + ','})
                else:
                    template.write({'email_to': user.email + ','})

                template.write({'body_html': self.comment})

            template.send_mail(purchase.id,force_send=True)
            purchase.write({'state': 'pendingops'})

        elif(self.type=='approve' and purchase.state == 'pendingops'):
            group = self.env['res.groups'].browse(self.env.ref('education.pos_group').id)
            for user in group.users:
                if(template.email_to):
                    template.write({'email_to': template.email_to + user.email + ','})
                else:
                    template.write({'email_to': user.email + ','})

                template.write({'body_html': self.comment})

            template.send_mail(purchase.id,force_send=True)
            purchase.button_approve()

        elif(self.type=='reject'):
            group = False
            if(purchase.state=='pendingbm'):
                group = self.env['res.groups'].browse(self.env.ref('education.ps_group').id)

            elif(purchase.state=='pendingcm'):
                group = self.env['res.groups'].browse(self.env.ref('education.bm_group').id)

            elif(purchase.state=='pendingacc'):
                group = self.env['res.groups'].browse(self.env.ref('education.country_management').id)

            for user in group.users:
                if(template.email_to):
                    template.write({'email_to': template.email_to + user.email + ','})
                else:
                    template.write({'email_to': user.email + ','})
                template.write({'body_html': self.comment})

            template.send_mail(purchase.id,force_send=True)
            purchase.write({'state': 'rejected'})

        elif(self.type=='return'):
            group = self.env['res.groups'].browse(self.env.ref('education.ps_group').id)
            for user in group.users:
                if(template.email_to):
                    template.write({'email_to': template.email_to + user.email + ','})
                else:
                    template.write({'email_to': user.email + ','})

                template.write({'body_html': self.comment})
            template.send_mail(purchase.id,force_send=True)
            purchase.write({'state': 'draft'})
