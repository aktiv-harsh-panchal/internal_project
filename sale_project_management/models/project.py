# -*- coding: utf-8 -*-

from odoo import api, models, fields


class Project(models.Model):
    _inherit = 'project.project'


    allocated_hours = fields.Float(
        compute='_compute_allocated_hours',
        store=True,
    )

    @api.depends('task_ids', 'task_ids.allocated_hours')
    def _compute_allocated_hours(self):
        """calculate allocated hours"""

        for project in self:
            project.allocated_hours = sum(
                project.task_ids.mapped('allocated_hours')
            )
