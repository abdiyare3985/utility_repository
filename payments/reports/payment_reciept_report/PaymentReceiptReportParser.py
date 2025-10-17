from odoo import models

class PaymentReceiptReportParser(models.AbstractModel):
    _name = 'report.payments.payment_reciept_report_pdf_template'
    _description = 'Payment Receipt Report Parser'

    # def _get_report_values(self, docids, data=None):
    #     #docs = self.env['payment.reciept.report.wizard'].browse(docids)
    #     print("Generating Payment Receipt Report...", data['payment_id'])
    #     paymentId = data.get('payment_id') if data else None
    #     if paymentId:
    #         payment = self.env['account.payment'].browse(paymentId)
    #         if payment.exists():
    #             return {
    #                 'docs': [payment],
    #             }
    #     return {
    #         'docs': None,
    #     }

    # def _get_report_values(self, docids, data=None):
    #     payment = None
    #     if data and data.get('payment_id'):
    #         payment = self.env['account.payment'].browse(data['payment_id'])
    #         print("Payment found via data:", payment)
    #     elif docids:
    #         print("No data, using docids:", docids)
    #         payment = self.env['account.payment'].browse(docids[0])
    #     return {
    #         'doc': payment if payment and payment.exists() else False,
    #     }

    def _get_report_values(self, docids, data=None):
     payment = None
     if data and data.get('payment_id'):
        print("Payment found")
        payment = self.env['account.payment'].browse(data['payment_id'])
     elif docids:
        payment = self.env['account.payment'].browse(docids[0])
     if payment and payment.exists():
        print("Returning payment:", payment)
        return {'doc': payment}
    # Do not include 'doc' key if not found
     return {}