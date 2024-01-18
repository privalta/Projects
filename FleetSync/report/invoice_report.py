# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pprint
from datetime import datetime
from pytz import timezone
from odoo import fields, models, tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
import calendar
from dateutil.relativedelta import relativedelta


class ReportInvoice(models.AbstractModel):
    _name = 'report.rapidusa.invoice'

    @api.model
    def _get_report_values(self, docsids, data=None):

        start_date = datetime.strptime(str(data['form']['date_start']), DATE_FORMAT)
        end_date = datetime.strptime(str(data['form']['date_end']), DATE_FORMAT)
        detail = data['form']['detail']
        inv = data['form']['inv']

        transfers = self.env['rapidusa.rapid_driver'].search([
            ('cr_date', '>=', start_date),
            ('cr_date', '<=', end_date)], order='cr_date')

        docs = {}
        aux = {}

        for i in transfers:
            date = str(i.cr_date)
            dispatch = i.dispatcher_id.name
            new={}

            j = {'transfer_id': i.transfer_id, 'route_id': i.route_id.route_name, 'cantidad': i.cars_total,
                 'unit_price': format(i.route_id.fee, ".2f"),
                 'amount': i.fees_related, 'cars': i.rapidcar_ids}

            # create a dict with dispatcher as the key for each record
            if dispatch not in new.keys():
                new[dispatch] = []
            new[dispatch].append(j)

            # add the dict to a new one with date as a key for each record
            # The structure would be date/dispatcher/transfer records
            if date not in docs.keys():
                docs[date] = []
            docs[date].append(new)

        # calculate totals
        for dates in docs: # a = date
            invoice = inv[dates]
            total = 0.00
            for dispatcher_list in docs[dates]:  # b = a_date/dispatcher
                for dispatcher in dispatcher_list:  # c = list of transfer_records
                    for record in dispatcher_list[dispatcher]:  # d single record
                        total += record['amount']
                        record['amount'] = format(record['amount'], ".2f")  # restructura el num a monetary
            inv_date = datetime.strptime(dates, DATE_FORMAT)  # convertir a en formato la fecha_invoice
            due_date = inv_date + relativedelta(days=31)  # c=due+date
            due_date_str = str(due_date.month)+'-'+str(due_date.day)+'-'+str(due_date.year)
            date_inv = str(inv_date.month)+'-'+str(inv_date.day)+'-'+str(inv_date.year)

            e = {'total': format(total, ".2f"),
                 'date_inv': date_inv,
                 'due_date': due_date_str,
                 'invoice': invoice,
                }

            if dates not in aux.keys():
                aux[dates] = []
            aux[dates].append(e)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_from': start_date,
            'date_to': end_date,
            'docs': docs,
            'aux': aux,
            'detail': detail,
        }

