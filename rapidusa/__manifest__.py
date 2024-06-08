# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Rapid USA",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/route_fees_data.xml",
        "data/rapidusa_data.xml",
        "data/product_data.xml",
        "data/hr_salary_rule_data.xml",
        "data/hr_payroll_structure_data.xml",
        "view/views.xml",
        "view/account_move_views.xml",
        "report/rapid_driver_report.xml",
        "report/rapid_driver_wizard.xml",
        "report/invoice_report.xml",
        "report/invoice_wizard.xml",
        "report/dispatcher_report.xml",
        "report/dispatcher_wizard.xml",
        "report/driver_hours_report.xml",
        "report/driver_hours_wizard.xml",
        "report/binding_reports.xml",
        "view/menu_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": True,
    "depends": ["base", "hr", "payroll_account"],
}
