# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _timesheet_create_project(self):
        """Reuse or create project based on partner"""
        self.ensure_one()

        partner = self.order_id.partner_id

        project = self.env['project.project'].search([
            ('name', '=', partner.name),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

        if not project:
            project = super()._timesheet_create_project()
            project.write({
                'name': partner.name,
                'partner_id': partner.id,
            })

        return project

    def _timesheet_create_task(self, project):
        """Create task under correct project with custom naming"""
        self.ensure_one()

        task = super()._timesheet_create_task(project)

        task.write({
            'name': "%s - %s" % (self.order_id.name, self.name),
            'date_deadline': fields.Datetime.now() + timedelta(hours=self.product_uom_qty),
            'allocated_hours': self.product_uom_qty,
        })

        return task
