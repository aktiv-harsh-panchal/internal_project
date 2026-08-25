# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ai_api_key = fields.Char(
        string="API Key",
        config_parameter="ai_invoice_agent.api_key",
    )
    ai_api_url = fields.Char(
        string="API URL",
        config_parameter="ai_invoice_agent.api_url",
    )
    ai_model = fields.Char(
        string="AI Model",
        config_parameter="ai_invoice_agent.model",
    )
    ai_batch_limit = fields.Integer(
        string="Batch Limit",
        default=50,
        config_parameter="ai_invoice_agent.batch_limit",
    )
    ai_reminder_gap_days = fields.Integer(
        string="Reminder Gap Days",
        default=7,
        config_parameter="ai_invoice_agent.reminder_gap_days",
    )
    ai_max_reminders = fields.Integer(
        string="Max Reminders",
        default=3,
        config_parameter="ai_invoice_agent.max_reminders",
    )