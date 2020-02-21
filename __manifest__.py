# -*- coding: utf-8 -*-
{
    'name': "openti",

    'summary': """
        This Module Add Functionalities for odoo nessery for OpenTI""",

    'description': """
        This Module Add Functionalities for odoo nessery for OpenTI
    """,

    'author': "Abiezer Sifontes",
    'website': "http://www.openti.cl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website_sale','l10n_cl_fe','l10n_cl_stock_picking'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'demo/payment_cron.xml',
        'demo/default_barcode_patterns.xml'
        'views/views.xml',
        'views/templates.xml',
        'views/commissions_invoice_clearence.xml',
        'views/account_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
