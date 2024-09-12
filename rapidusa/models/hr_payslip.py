from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def compute_sheet(self):
        for payslip in self:
            payslip.worked_days_line_ids.unlink()
            payslip.input_line_ids.unlink()
            attendances = self.env["rapidusa.attendances"].search(
                [
                    ("cr_date", ">=", payslip.date_from.strftime(DF)),
                    ("cr_date", "<=", payslip.date_to.strftime(DF)),
                ]
            )
            workers = attendances.workers_ids.filtered(lambda r: r.employee_id == payslip.employee_id)
            a = workers.filtered(lambda r: r.worker_role_id.name == "Lead Clean")
            b = workers.filtered(lambda r: r.worker_role_id.name != "Lead Clean")
            c = []
            for i in b:
                if i.worker_role_id.name not in c:
                    c.append(i.worker_role_id.name)

            if not payslip.employee_id.contract_id:
                raise UserError(_("The employee does not have a contract active.") + payslip.employee_id.name)
            if len(workers) > 0:
                if len(a) > 0:
                    car_total = 0
                    for j in a:
                        car_total += j.rapid_attendances_id.car_count
                    self.env["hr.payslip.input"].create(
                        {
                            "name": "Attendances",
                            "payslip_id": payslip.id,
                            "sequence": 1,
                            "code": "Lead_Clean",
                            "amount": 0,
                            "amount_qty": car_total,
                            "contract_id": payslip.employee_id.contract_id.id,
                        }
                    )
                if len(b) > 0:
                    for k in c:
                        number_of_hours = 0
                        for j in b.filtered(lambda r: r.worker_role_id.name == k):
                            number_of_hours += j.rapid_attendances_id.worked_hours
                        self.env["hr.payslip.worked_days"].create(
                            {
                                "name": "Attendances",
                                "payslip_id": payslip.id,
                                "sequence": 1,
                                "number_of_hours": number_of_hours,
                                "code": k.replace(" ", "_"),
                                "number_of_days": 0,
                                "contract_id": payslip.employee_id.contract_id.id,
                            }
                        )
            # drivers = self.env["rapidusa.rapid_driver"].search(
            #     [
            #         ("acc_status", "=", "Paid"),
            #         ("cr_date", ">=", payslip.date_from.strftime(DF)),
            #         ("cr_date", "<=", payslip.date_to.strftime(DF)),
            #     ]
            # )
            # service = {
            #     "vehicle_transfers": "Vehicle Transfers",
            #     "car_wash_special_cleaner": "Car Wash (Special Cleaner)",
            #     "car_wash_regular_cleaner": "Car Wash (Regular Cleaner)",
            #     "drive_allocation": "Drive Allocation",
            # }
            # for i in drivers:
            #     for j in i.workers_ids:
            #         if payslip.employee_id.id == j.employee_id.id:
            #             if not j.employee_id.contract_id:
            #                 raise UserError(_("The employee does not have a contract active.") + j.employee_id.name)
            #             if j.worker_role_id.name == "Lead Clean":
            #                 self.env["hr.payslip.input"].create(
            #                     {
            #                         "name": service[i.car_service_id],
            #                         "payslip_id": payslip.id,
            #                         "sequence": 1,
            #                         "code": j.worker_role_id.name.replace(" ", "_"),
            #                         "amount": 0,
            #                         "amount_qty": i.cars_total,
            #                         "contract_id": j.employee_id.contract_id.id,
            #                     }
            #                 )
            #             else:
            #                 self.env["hr.payslip.worked_days"].create(
            #                     {
            #                         "name": service[i.car_service_id],
            #                         "payslip_id": payslip.id,
            #                         "sequence": 1,
            #                         "number_of_hours": i.trayecto_hrs,
            #                         "code": j.worker_role_id.name.replace(" ", "_"),
            #                         "number_of_days": 0,
            #                         "contract_id": j.employee_id.contract_id.id,
            #                     }
            #                 )

            super(HrPayslip, payslip).compute_sheet()
        return True
