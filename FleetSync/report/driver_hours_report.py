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
    _name = 'report.rapidusa.driver_hours'

    @api.model
    def _get_report_values(self, docsids, data=None):
        start_date = datetime.strptime(str(data['form']['date_start']), DATE_FORMAT)
        end_date = datetime.strptime(str(data['form']['date_end']), DATE_FORMAT)
        fee = data['form']['fee']

        transfers = self.env['rapidusa.attendances'].search([
            ('check_in', '>=', start_date),
            ('check_in', '<=', end_date)])

        drivers = self.env['hr.employee'].search([])
        docs = {}

        for driver in drivers:
            for i in transfers:
                for att in i.employees_id:
                    if driver == att:
                        if driver not in docs.keys():
                            docs[driver] = []
                        j = {"check_in": i.check_in.date(), "worked_hours": format(i.worked_hours,".2f")}
                        docs[driver].append(j)
        aux = {}
        suma = 0
        for i in docs:
            total = 0
            for j in docs[i]:
                total += float(j['worked_hours'])
            if i not in aux.keys():
                aux[i] = []

            j = {'total': format(total,".2f"), 'fee': format(total*fee,".2f")}
            aux[i].append(j)
            suma += float(total)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
            'aux': aux,
            'fee': format(fee,".2f"),
            'suma': format(suma*fee,".2f"),
            'date_from': start_date,
            'date_to': end_date
        }
