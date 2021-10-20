# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

# import models
from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def total_debit_credit(self):
        res = {}
        for move in self:
            dr_total = 0.0
            cr_total = 0.0
            for line in move.line_ids:
                dr_total += line.debit
                cr_total += line.credit
            res.update({'dr_total': dr_total, 'cr_total': cr_total})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    _sql_constraints = [
        (
            'check_credit_debit',
            'CHECK(1=1)',
            'Wrong credit or debit value in accounting entry !'
        ),

        (
            'check_accountable_required_fields',
            "CHECK(COALESCE(display_type IN ('line_section', 'line_note'), 'f') OR account_id IS NOT NULL)",
            "Missing required account on accountable invoice line."
        ),

        (
            'check_non_accountable_fields_null',
            "CHECK(display_type NOT IN ('line_section', 'line_note') OR (amount_currency = 0 AND debit = 0 AND credit = 0 AND account_id IS NULL))",
            "Forbidden unit price, account and quantity on non-accountable invoice line"
        ),

    ]
    # (
    #     'check_amount_currency_balance_sign',
    #     '''CHECK(
    #     currency_id IS NULL
    #     OR
    #     company_currency_id IS NULL
    #     OR
    #     (
    #     (currency_id != company_currency_id)
    #     AND
    #     (
    #     (balance > 0 AND amount_currency > 0)
    #     OR (balance <= 0 AND amount_currency <= 0)
    #     OR (balance >= 0 AND amount_currency >= 0)
    #     )
    #     )
    #     )''',
    #     "The amount expressed in the secondary currency must be positive when account is debited and negative when account is credited. Moreover, the currency field has to be left empty when the amount is expressed in the company currency."
    # ),
