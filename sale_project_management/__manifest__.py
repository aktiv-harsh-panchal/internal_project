# -*- coding: utf-8 -*-

{
    'name': 'Sale Project Management',
    'version': '19.0.1.0.0',
    'summary': 'Create project and tasks from sale order',
    'description': """
        Create a project for the customer when a Sale Order is confirmed.
        - If the customer already has a project, reuse the existing project.
        - Create tasks based on Sale Order line descriptions.
        - Planned hours of the task are taken from the Sale Order line quantity (UoM Hours).
    """,
    'author': 'Harsh Panchal',
    'website': "https://www.aktivsoftware.com/",
    'category': 'Sales/Project',
    'depends': [
        'hr_timesheet',
        'sale_project',
    ],
    'data': [
        'views/project_view.xml',
        'views/res_partner_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
