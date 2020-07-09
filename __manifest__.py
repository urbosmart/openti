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
    'depends': [
        'website_sale',
        'l10n_cl_fe',
        'l10n_cl_dte_point_of_sale',
        'l10n_cl_stock_picking',
        'payment_webpay',
        'payment_khipu',
        'tecnopti',
        'web_responsive',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/inherit_report_paperformat.xml',
        # 'data/promotion_modules.xml',
        # 'demo/payment_cron.xml',
        # 'demo/default_barcode_patterns.xml',
        # 'demo/stock_data.xml',
        'report/inherit_report_pos_common_templates.xml',
        'report/inherit_invoice_layout.xml',
        'views/commissions_invoice_clearence.xml',
        'views/account_invoice.xml',
        'views/tiendas.xml',
        'views/auth_signup_login_templates.xml',
        'views/address.xml',
        'views/assets_frontend.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'qweb':[
    ],
    'auto_install': True,
    'application': True,
    'bootstrap': True,
}
