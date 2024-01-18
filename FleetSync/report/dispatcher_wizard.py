# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO, FR
import pytz


class ReportDispatcherWizard(models.TransientModel):
    _name = 'rapidusa.dispatcher_wizard'
    _description = 'RapidUSA Movements Report by Dispatcher'

    a = datetime.now(pytz.timezone("US/Eastern")) + relativedelta(weekday=MO(-1))
    b = datetime.now(pytz.timezone("US/Eastern")) + relativedelta(weekday=FR(1))
    start = fields.Date('From', default=a, required=True)
    end = fields.Date('To', default=b, required=True)
    dispatcher = fields.Many2one('rapidusa.dispatch', 'Dispatched by:', required=True)
    details = fields.Boolean('Detail Report?')

    def action_print(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.start,
                'date_end': self.end,
                'dispatcher': self.dispatcher.id,
                'dispatcher_name': self.dispatcher.name,
                'detail': self.details,
            },
        }
        return self.env.ref('rapidusa.action_report_dispatcher').report_action(self, data=data)
