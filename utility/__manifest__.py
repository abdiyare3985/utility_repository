{
    'name': 'Utility',
    'version': '17.0.1.0.0',
    'summary': 'A collection of useful utilities and helpers for Odoo 17.',
    'description': 'This module provides reusable utilities for Odoo development.',
    'author': 'Your Company Name',
    'website': 'https://yourcompany.com',
    'category': 'Tools',
    'depends': ['base','crm','account', 'mail','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/utility_menus.xml',
        'views/meter_zones_views.xml',
        'views/utility_meter_views.xml',
        'views/crm_lead_views.xml',
        'wizard/customerregisteration/create_customer_meter_wizard_views.xml',
        'views/meter_serials_views.xml',
        'views/meter_discounts_views.xml',
        'views/meter_groups_views.xml',
        'views/bill_plans_views.xml',
        'views/meter_readings_view.xml',
        'views/customer_views.xml',
        'views/account_move_inherit_views.xml',
        'views/res_users_inherit_view.xml',

        'wizard/meter_status_changes/meter_status_reason_wizard_view.xml',
        'wizard/reports/meter_list_report_wizard_view.xml',
        'wizard/reports/meter_invoices/invoice_report_wizard_view.xml',
        'wizard/reports/meter_reading/meter_reading_report_views.xml',
        
        #Reports
        
        'reports/meter_list_report/report_template.xml',
        'reports/meter_list_report/report_action.xml',

        'reports/meter_invoice/report_template.xml',
        'reports/meter_invoice/report_action.xml',

        'reports/meter_reading/report_template.xml',
        'reports/meter_reading/report_action.xml',
        

        
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}