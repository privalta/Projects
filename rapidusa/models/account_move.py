from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    rapid_driver_id = fields.Many2one("rapidusa.rapid_driver")
