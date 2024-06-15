from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def compute_sheet(self):
        for payslip in self:
            payslip.worked_days_line_ids.unlink()
            payslip.input_line_ids.unlink()
            drivers = self.env["rapidusa.rapid_driver"].search(
                [
                    ("acc_status", "=", "Paid"),
                    ("cr_date", ">=", payslip.date_from.strftime(DF)),
                    ("cr_date", "<=", payslip.date_to.strftime(DF)),
                    ("workers_ids.employee_id", "=", payslip.employee_id.id),
                ]
            )
            service = {
                "vehicle_transfers": "Vehicle Transfers",
                "car_wash_special_cleaner": "Car Wash (Special Cleaner)",
                "car_wash_regular_cleaner": "Car Wash (Regular Cleaner)",
                "drive_allocation": "Drive Allocation",
            }
            for i in drivers:
                for j in i.workers_ids:
                    if payslip.employee_id.id == j.employee_id.id:
                        if not j.employee_id.contract_id:
                            raise UserError(_("The employee does not have a contract active.") + j.employee_id.name)
                        if j.worker_role_id.name == "Lead Clean":
                            self.env["hr.payslip.input"].create(
                                {
                                    "name": service[i.car_service_id],
                                    "payslip_id": payslip.id,
                                    "sequence": 1,
                                    "code": j.worker_role_id.name.replace(" ", "_"),
                                    "amount": 0,
                                    "amount_qty": i.cars_total,
                                    "contract_id": j.employee_id.contract_id.id,
                                }
                            )
                        else:
                            self.env["hr.payslip.worked_days"].create(
                                {
                                    "name": service[i.car_service_id],
                                    "payslip_id": payslip.id,
                                    "sequence": 1,
                                    "number_of_hours": i.trayecto_hrs,
                                    "code": j.worker_role_id.name.replace(" ", "_"),
                                    "number_of_days": 0,
                                    "contract_id": j.employee_id.contract_id.id,
                                }
                            )
            attendances = self.env["rapidusa.attendances"].search(
                [
                    ("cr_date", ">=", payslip.date_from.strftime(DF)),
                    ("cr_date", "<=", payslip.date_to.strftime(DF)),
                ]
            )
            for j in attendances:
                for employee in j.employees_id:
                    if payslip.employee_id.id == employee.id:
                        self.env["hr.payslip.worked_days"].create(
                            {
                                "name": "Attendances",
                                "payslip_id": payslip.id,
                                "sequence": 1,
                                "number_of_hours": j.worked_hours,
                                "code": "Attendances",
                                "number_of_days": 0,
                                "contract_id": employee.contract_id.id,
                            }
                        )
            super(HrPayslip, payslip).compute_sheet()
        return True
