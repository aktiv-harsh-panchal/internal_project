# -*- coding: utf-8 -*-
from odoo import fields, models


class AIOverdueInvoiceLog(models.Model):
    _name = "ai.overdue.invoice.log"
    _description = "AI Overdue Invoice Reminder Log"
    _order = "sent_date desc, id desc"

    invoice_id = fields.Many2one("account.move", string="Invoice", required=True, ondelete="cascade", index=True)
    partner_id = fields.Many2one("res.partner", string="Customer", related="invoice_id.partner_id", store=True, index=True)
    company_id = fields.Many2one("res.company", string="Company", related="invoice_id.company_id", store=True, index=True)
    sent_date = fields.Datetime(string="Sent On", default=fields.Datetime.now, required=True, index=True)
    reminder_level = fields.Integer(string="Reminder Level", required=True, default=1, index=True)
    overdue_days = fields.Integer(string="Overdue Days", required=True, default=0)
    email_to = fields.Char(string="Email To")
    subject = fields.Char(string="Subject")
    ai_prompt = fields.Text(string="AI Prompt")
    ai_response = fields.Text(string="AI Response")
    body = fields.Html(string="Email Body")
    state = fields.Selection([
        ("sent", "Sent"),
        ("skipped", "Skipped"),
        ("failed", "Failed"),
        ("activity", "Activity Created"),
    ], default="sent", required=True, index=True)
    message = fields.Text(string="Message")
