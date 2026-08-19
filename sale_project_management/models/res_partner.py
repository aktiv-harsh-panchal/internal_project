# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    project_count = fields.Integer(
        string="Projects",
        compute="_compute_project_count"
    )

    def _compute_project_count(self):
        """count project"""
        for partner in self:
            projects = self.env['project.project'].search([
                ('partner_id', '=', partner.id)
            ])
            partner.project_count = len(projects)

    def action_view_projects(self):
        """open project view for customer"""
        return {
            'name': 'Projects',
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }
