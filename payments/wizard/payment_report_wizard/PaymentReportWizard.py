from odoo import models, fields, api

class PaymentReportWizard(models.TransientModel):
    _name = 'payment.report.wizard'
    _description = 'Payment Report Wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    customer_id = fields.Many2one('res.partner', string="Customer",
                      domain="[('customer_rank', '>', 0)]"            
                                  )

    # def action_show_report(self):
    #     domain = [
    #         ('date', '>=', self.date_from),
    #         ('date', '<=', self.date_to),
    #     ]
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Payments',
    #         'res_model': 'account.payment',
    #         'view_mode': 'tree,form',
    #         'domain': domain,
    #         'target': 'current',
    #     }

    def action_show_report(self):
     return self.env.ref('payments.payment_report_pdf').report_action(self)
    
    def action_print_summary_pdf(self):
        return self.env.ref('payments.payment_report_summary_pdf').report_action(self)
   
   
    def action_print_user_date_pdf(self):
        return self.env.ref('payments.payment_report_by_user_summary_pdf').report_action(self)