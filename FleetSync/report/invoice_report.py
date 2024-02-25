# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pprint
from datetime import datetime
from pytz import timezone
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import calendar
from dateutil.relativedelta import relativedelta
from collections import defaultdict


class ReportInvoice(models.AbstractModel):
    _name = 'report.rapidusa.invoice'


    @api.model
    def _get_report_values(self, docsids, data=None):

        start_date = datetime.strptime(str(data['form']['date_start']), DATE_FORMAT)
        end_date = datetime.strptime(str(data['form']['date_end']), DATE_FORMAT)
        detail = data['form']['detail']
        invoice_from = data['form']['inv']

        transfers = self.env['rapidusa.rapid_driver'].search([
            ('cr_date', '>=', start_date),
            ('cr_date', '<=', end_date)], order='cr_date')
        
        docs={}
        invoice = invoice_from - 1

        for i in transfers:
            invoice += 1
            invoice_no = 'INV-' + str(invoice)
            # inv_date = datetime.strptime(i.cr_date, DATE_FORMAT)
            date_inv = str(i.cr_date.month) + '-' + str(i.cr_date.day) + '-' + str(i.cr_date.year)
            due_date = i.cr_date + relativedelta(days=31)
            due_date_str = str(due_date.month) + '-' + str(due_date.day) + '-' + str(due_date.year)

            j = {'transfer_id': i.transfer_id, 'dispatcher':i.dispatcher_id.name, 'route': i.route_id.route_name,
                 'cars_total': i.cars_total, 'unit_price':i.route_id.fee, 'cars': i.rapidcar_ids, 'fees': i.fees_related,
                 'date_inv': date_inv, 'due_date': due_date_str}

            # create a dict with route as the key for each record
            if invoice_no not in docs.keys():
                docs[invoice_no] = []
            docs[invoice_no].append(j)


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': start_date,
            'date_to': end_date,
            'docs': docs,
            'detail': detail,
        }

