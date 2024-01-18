# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO, FR
import pytz


class ReportInvoiceWizard(models.TransientModel):
    _name = 'rapidusa.invoice_wizard'
    _description = 'RapidUSA Invoices'

    a = datetime.now(pytz.timezone("US/Eastern")) + relativedelta(weekday=MO(-1))
    b = datetime.now(pytz.timezone("US/Eastern")) + relativedelta(weekday=FR(1))
    start = fields.Date('From', default=a, required=True)
    end = fields.Date('To', default=b, required=True)
    detail = fields.Boolean('List Vehicles?', default = True)
    inve = fields.Integer('Invoice Number', default=0)


    def action_print(self):

        inv={}
        invent = self.inve-1
        transfers = self.env['rapidusa.rapid_driver'].search([
            ('cr_date', '>=', self.start),
            ('cr_date', '<=', self.end)], order='cr_date')

        for i in transfers:
            date = str(i.cr_date)
            if date not in inv.keys():
                inv[date] = []

        for j in inv:
            invent += 1
            inv[j] = 'INV-' + str(invent)

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.start,
                'date_end': self.end,
                'detail': self.detail,
                'inv': inv,


            },
        }
        return self.env.ref('rapidusa.action_report_invoice').report_action(self, data=data)
