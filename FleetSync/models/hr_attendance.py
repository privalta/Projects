# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from datetime import datetime
import pytz


class HrAttendance(models.Model):
    _name = 'rapidusa.attendances'
    _description = 'Attendances'

    employees_id = fields.Many2many('hr.employee', string="Employees")
    cr_date = fields.Date('Create Date', default=lambda self: datetime.now(pytz.timezone("US/Eastern")))
    check_in = fields.Datetime(string="Check In", default=lambda self: datetime.today(),
                               required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    workers = fields.Integer('Employees', compute='_compute_workers')

    @api.depends('employees_id', 'workers')
    def _compute_workers(self):
        total = 0
        for i in self:
            for j in i.employees_id:
                total += 1
            i.workers = total

    def do_check_out(self):
        for i in self:
            if i.check_in:
                i.check_out = datetime.today()
            else:
                raise exceptions.ValidationError(_('"Check Out cannot be mark before Check In"'))

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = round(delta.total_seconds() / 3600.0,2)
            else:
                attendance.worked_hours = 0

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                if attendance.check_out < attendance.check_in:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))
