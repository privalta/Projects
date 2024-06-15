# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class ReportInvoiceNoBilled(models.AbstractModel):
    _name = "report.rapidusa.invoice_no_billed"
    _description = "Report Invoice no Billed"

    @api.model
    def _get_report_values(self, docsids, data=None):
        start_date = datetime.strptime(str(data["form"]["date_start"]), DATE_FORMAT)
        end_date = datetime.strptime(str(data["form"]["date_end"]), DATE_FORMAT)
        detail = data["form"]["detail"]
        acc_status = data["form"]["acc_status"]
        transfers = self.env["rapidusa.rapid_driver"].search([("cr_date", ">=", start_date), ("cr_date", "<=", end_date), ("acc_status", "in", acc_status.split(","))], order="cr_date")
        docs = []
        for i in transfers:
            date_inv = str(i.cr_date.month) + "-" + str(i.cr_date.day) + "-" + str(i.cr_date.year)
            due_date = i.cr_date + relativedelta(days=31)
            due_date_str = str(due_date.month) + "-" + str(due_date.day) + "-" + str(due_date.year)
            invoice = self.env["account.move"].search([("rapid_driver_id", "=", i.id)])
            for k in invoice:
                j = {
                    "invoice_no": k.payment_reference,
                    "transfer": i.transfer,
                    "dispatcher": i.dispatcher_id.name,
                    "route": i.route_id.route_name,
                    "cars_total": i.cars_total,
                    "unit_price": i.route_id.fee,
                    "cars": i.rapidcar_ids,
                    "fees": i.fees_related,
                    "date_inv": date_inv,
                    "due_date": due_date_str,
                }
                docs.append(j)
        return {
            "doc_ids": data["ids"],
            "doc_model": data["model"],
            "date_from": start_date,
            "date_to": end_date,
            "docs": docs,
            "detail": detail,
        }
