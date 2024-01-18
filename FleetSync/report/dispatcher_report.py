# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pprint
from datetime import datetime
from pytz import timezone
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import calendar
from dateutil.relativedelta import relativedelta


class ReportDispatcher(models.AbstractModel):
    _name = 'report.rapidusa.dispatcher'

    @api.model
    def _get_report_values(self, docsids, data=None):
        start_date = datetime.strptime(str(data['form']['date_start']), DATE_FORMAT)
        end_date = datetime.strptime(str(data['form']['date_end']), DATE_FORMAT)
        dispatcher = data['form']['dispatcher']
        dispatcher_name = data['form']['dispatcher_name']
        detail = data['form']['detail']
        a = False

        transfers = self.env['rapidusa.rapid_driver'].search([
            ('cr_date', '>=', start_date),
            ('cr_date', '<=', end_date),
            ('dispatcher_id', '=', dispatcher)])

        if len(transfers) == 0:
            a = True

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': start_date.date(),
            'date_to': end_date.date(),
            'dispatch': dispatcher,
            'dispatcher_name': dispatcher_name,
            'detail': detail,
            'docs': transfers,
            'a': a,
        }
