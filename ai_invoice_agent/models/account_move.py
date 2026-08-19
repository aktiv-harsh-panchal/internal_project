# -*- coding: utf-8 -*-
import json
import logging
import requests

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _ai_invoice_get_param(self, key, default=False):
        return self.env["ir.config_parameter"].sudo().get_param(
            "ai_invoice_agent.%s" % key,
            default,
        )

    def _ai_invoice_int_param(self, key, default):
        try:
            return int(self._ai_invoice_get_param(key, default))
        except Exception:
            return default

    def _ai_overdue_build_prompt(self, invoice, reminder_level, overdue_days):
        return """You are an accounts receivable assistant.
            Write a professional payment reminder email for an overdue customer invoice.
            
            Rules:
            - Return JSON only with keys: subject, body_html
            - body_html must be valid simple HTML
            - Do not invent payment links or bank details
            - Tone by reminder level:
              1 = polite reminder
              2 = firm follow-up
              3 = final notice before manual follow-up
            - Keep it short and clear
            
            Invoice context:
            Customer: {customer}
            Invoice Number: {invoice}
            Due Date: {due_date}
            Overdue Days: {overdue_days}
            Residual Amount: {amount} {currency}
            Reminder Level: {level}
            Company: {company}
            """.format(
            customer=invoice.partner_id.display_name,
            invoice=invoice.name or invoice.ref or invoice.id,
            due_date=invoice.invoice_date_due,
            overdue_days=overdue_days,
            amount=invoice.amount_residual,
            currency=invoice.currency_id.name or "",
            level=reminder_level,
            company=invoice.company_id.name,
        )

    def _ai_overdue_generate_email(self, invoice, reminder_level, overdue_days):
        api_key = self._ai_invoice_get_param("api_key")
        api_url = self._ai_invoice_get_param("api_url")
        model = self._ai_invoice_get_param("model")

        if not api_key:
            raise Exception(_("AI API Key is not configured."))
        if not api_url:
            raise Exception(_("AI API URL is not configured."))
        if not model:
            raise Exception(_("AI Model is not configured."))

        prompt = self._ai_overdue_build_prompt(invoice, reminder_level, overdue_days)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate safe, professional overdue invoice reminder emails.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.3,
        }

        headers = {
            "Authorization": "Bearer %s" % api_key,
            "Content-Type": "application/json",
        }

        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30,
        )
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"].strip()
    
        if content.startswith("```"):
            content = content.strip("`")
            content = content.replace("json\n", "", 1).replace("json", "", 1).strip()

        data = json.loads(content)

        return prompt, content, data.get("subject"), data.get("body_html")

    def _ai_overdue_create_activity(self, invoice):
        invoice.activity_schedule(
            "mail.mail_activity_data_todo",
            summary=_("Manual follow-up required for overdue invoice"),
            note=_("Maximum AI reminders reached. Please contact the customer manually."),
            user_id=invoice.invoice_user_id.id or self.env.user.id,
        )

    def cron_ai_overdue_invoice_agent(self):
        today = fields.Date.context_today(self)

        batch_limit = self._ai_invoice_int_param("batch_limit", 50)
        gap_days = self._ai_invoice_int_param("reminder_gap_days", 7)
        max_reminders = self._ai_invoice_int_param("max_reminders", 3)

        domain = [
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("payment_state", "not in", ("paid", "reversed")),
            ("invoice_date_due", "<", today),
            ("partner_id.email", "!=", False),
        ]

        invoices = self.search(
            domain,
            order="invoice_date_due asc, id asc",
            limit=batch_limit,
        )

        Log = self.env["ai.overdue.invoice.log"].sudo()

        for invoice in invoices:
            logs = Log.search(
                [("invoice_id", "=", invoice.id)],
                order="sent_date desc",
            )

            sent_logs = logs.filtered(lambda log: log.state == "sent")
            reminder_level = len(sent_logs) + 1
            overdue_days = (
                (today - invoice.invoice_date_due).days
                if invoice.invoice_date_due
                else 0
            )

            if reminder_level > max_reminders:
                if not logs.filtered(lambda log: log.state == "activity"):
                    self._ai_overdue_create_activity(invoice)
                    Log.create({
                        "invoice_id": invoice.id,
                        "reminder_level": reminder_level,
                        "overdue_days": overdue_days,
                        "email_to": invoice.partner_id.email,
                        "state": "activity",
                        "message": "Maximum reminders reached. Internal activity created.",
                    })
                continue

            if sent_logs:
                last_sent = fields.Date.to_date(sent_logs[0].sent_date)
                if (today - last_sent).days < gap_days:
                    continue

            try:
                prompt, ai_response, subject, body = self._ai_overdue_generate_email(
                    invoice,
                    reminder_level,
                    overdue_days,
                )

                if not subject or not body:
                    raise Exception("AI response missing subject/body_html.")

                mail = self.env["mail.mail"].sudo().create({
                    "subject": subject,
                    "body_html": body,
                    "email_to": invoice.partner_id.email,
                    "auto_delete": False,
                    "model": "account.move",
                    "res_id": invoice.id,
                })
                mail.send()

                Log.create({
                    "invoice_id": invoice.id,
                    "reminder_level": reminder_level,
                    "overdue_days": overdue_days,
                    "email_to": invoice.partner_id.email,
                    "subject": subject,
                    "body": body,
                    "ai_prompt": prompt,
                    "ai_response": ai_response,
                    "state": "sent",
                    "message": "AI email sent successfully.",
                })

            except Exception as e:
                _logger.exception(
                    "AI invoice reminder failed for invoice %s",
                    invoice.id,
                )
                Log.create({
                    "invoice_id": invoice.id,
                    "reminder_level": reminder_level,
                    "overdue_days": overdue_days,
                    "email_to": invoice.partner_id.email,
                    "state": "failed",
                    "message": str(e),
                })