# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api
from odoo.tools import date_utils

class AccountReport(models.AbstractModel):

    _inherit='account.report'

    @api.model
    def _init_filter_date(self, options, previous_options=None):
        if self.filter_date is None:
            return
        previous_date = (previous_options or {}).get('date', {})

        # Default values.
        mode = previous_date.get('mode') or self.filter_date.get('mode', 'range')
        options_filter = previous_date.get('filter') or self.filter_date.get('filter') or (
            'today' if mode == 'single' else 'fiscalyear')
        date_from = fields.Date.to_date(previous_date.get('date_from') or self.filter_date.get('date_from'))
        date_to = fields.Date.to_date(previous_date.get('date_to') or self.filter_date.get('date_to'))
        strict_range = previous_date.get('strict_range', False)

        # Create date option for each company.

        if previous_options and previous_options.get('date'):
            strict_range = (previous_options and previous_options.get('date').get('strict_range'))
        if previous_options and previous_options.get('date') and previous_options['date'].get('filter') and not (previous_options['date']['filter'] == 'today' and mode == 'range'):
            options_filter = previous_options['date']['filter']
            if options_filter == 'custom':
                if previous_options['date']['date_from'] and mode == 'range':
                    date_from = fields.Date.from_string(previous_options['date']['date_from'])
                if previous_options['date']['date_to']:
                    date_to = fields.Date.from_string(previous_options['date']['date_to'])

        period_type = False
        if 'today' in options_filter:
            date_to = fields.Date.context_today(self)
            date_from = date_utils.get_month(date_to)[0]

        elif 'month' in options_filter:
            date_from, date_to = date_utils.get_month(fields.Date.context_today(self))
            period_type = 'month'

        elif 'quarter' in options_filter:
            date_from, date_to = date_utils.get_quarter(fields.Date.context_today(self))
            period_type = 'quarter'

        elif 'year' in options_filter:
            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Date.context_today(self))
            date_from = company_fiscalyear_dates['date_from']
            date_to = company_fiscalyear_dates['date_to']

        elif not date_from:
            date_from = date_utils.get_month(date_to)[0]

        options['date'] = self._get_dates_period(options, date_from, date_to, mode, period_type=period_type, strict_range=strict_range)
        if 'last' in options_filter:
            options['date'] = self._get_dates_previous_period(options, options['date'])

        options['date']['filter'] = options_filter
