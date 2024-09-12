from odoo import _, api, fields, models
from odoo.tools import get_lang

# from odoo.tools.misc import get_lang


class AccountMove(models.Model):
    _inherit = "account.move"

    rapid_driver_id = fields.Many2one("rapidusa.rapid_driver")
    dispatcher_id = fields.Many2one("rapidusa.dispatch", "Dispatched by", required=True, default=lambda self: self.rapid_driver_id.dispatcher_id)

    def action_invoice_report_sent(self):
        """Open a window to compose an email, with the edi invoice template
        message loaded by default
        """
        self.ensure_one()
        template = self.env.ref("rapidusa.email_template_invoice_rapid_usa_report", raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref("account.account_invoice_send_wizard_form", raise_if_not_found=False)
        ctx = dict(
            default_model="account.move",
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model="account.move",
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True,
        )
        return {
            "name": _("Send Invoice"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.invoice.send",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    @api.depends("posted_before", "state", "journal_id", "date")
    def _compute_name(self):
        self.ensure_one()
        for move in self:
            super(AccountMove, move)._compute_name()
            if move.name and move.name != "/" and move.state == "posted":
                seq = self.env["ir.sequence"].next_by_code("inv_account_move")
                move.name = seq
            if move.name and move.name != "/" and move.state == "draft":
                move.name = "Draft"
        return
