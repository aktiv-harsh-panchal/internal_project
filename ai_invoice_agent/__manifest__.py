# -*- coding: utf-8 -*-
{
    "name": "AI Invoice Agent",
    "version": "19.0.1.0.3",
    "category": "Accounting",
    "summary": "AI powered overdue invoice reminder automation",
    "depends": ["account", "mail"],
    "images": ["static/description/icon.png"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/res_config_settings_views.xml",
        "views/ai_overdue_invoice_log_views.xml",
    ],
    "installable": True,    
    "application": True,
    "license": "LGPL-3",
}
