# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pprint
from datetime import datetime
from pytz import timezone
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ReportRapidDriver(models.AbstractModel):
    _name = 'report.rapidusa.rapid_driver'

    @api.model
    def _get_report_values(self, docsids, data=None):
        start_date = datetime.strptime(str(data['form']['date_start']), DATE_FORMAT)
        end_date = datetime.strptime(str(data['form']['date_end']), DATE_FORMAT)
        detail = data['form']['detail']
        a = False

        transfers = self.env['rapidusa.rapid_driver'].search([
            ('cr_date', '>=', start_date),
            ('cr_date', '<=', end_date)])

        if len(transfers) == 0:
            a = True
        docs = {}

        for i in transfers:
            date = str(i.cr_date)

            if date not in docs.keys():
                docs[date] = []

            j = {'route_id': i.route_id.route_name, 'date': date, 'cantidad': i.cars_total,
                 'unit_price': format(i.route_id.fee, ".2f"),
                 'amount': i.fees_related, 'cars': i.rapidcar_ids}

            docs[date].append(j)


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': start_date.date(),
            'date_to': end_date.date(),
            'docs': docs,
            'detail': detail,
            'a': a,

        }
