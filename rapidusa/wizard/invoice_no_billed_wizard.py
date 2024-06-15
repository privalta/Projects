# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

import pytz
from dateutil.relativedelta import FR, MO, relativedelta
from odoo import fields, models


class ReportInvoiceWizard(models.TransientModel):
    _name = "rapidusa.invoice_no_billed_wizard"
    _description = "RapidUSA Invoices"

    a = datetime.now(pytz.timezone("US/Eastern")) + relativedelta(weekday=MO(-1))
    b = datetime.now(pytz.timezone("US/Eastern")) + relativedelta(weekday=FR(1))
    start = fields.Date("From", default=a, required=True)
    end = fields.Date("To", default=b, required=True)
    detail = fields.Boolean("List Vehicles?", default=True)
    acc_status = fields.Selection([("Draft,Paid", "No Billed (Draft-Paid)"), ("Draft", "Draft"), ("Billed", "Billed"), ("Paid", "Paid")], default="Draft,Paid", required=True)

    def action_print(self):
        data = {
            "ids": self.ids,
            "model": self._name,
            "form": {
                "date_start": self.start,
                "date_end": self.end,
                "detail": self.detail,
                "acc_status": self.acc_status,
            },
        }
        return self.env.ref("rapidusa.action_report_invoice_no_billed").report_action(self, data=data)
