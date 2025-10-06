{
    'name': 'E-Payment',
    'version': '17.0.1.0.0',
    'summary': 'Electronic payment for customer invoices',
    'description': 'Module to handle electronic payments for customer invoices.',
    'category': 'Accounting',
    'author': 'Your Name',
    'depends': ['account','utility'],
    'data': [
        # Add your views, security, etc. here
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/account_payment_inherit_views.xml',
        'views/sahal_imports_views.xml',

        'wizard/payment_report_wizard/payment_report_wizard_views.xml',

        'reports/payment_report/payment_report_templates.xml',
        'reports/payment_report/payment_report_actions.xml',

        'reports/payment_report_summary/payment_report_summary_templates.xml',
        'reports/payment_report_summary/payment_report_summary_actions.xml',

        'reports/payment_report_user_summary/payment_report_by_user_summary_templates.xml',
        'reports/payment_report_user_summary/payment_report_by_user_summary_actions.xml',
      
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}