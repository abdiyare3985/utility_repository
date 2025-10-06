from odoo import models

class ReportCustomInvoice(models.AbstractModel):
    _name = 'report.utility.report_custom_invoice_document'
    _description = 'Custom Invoice Report'

    def _get_previous_balance(self, invoice):
        # Compute previous balance as of invoice date
        domain = [
            ('partner_id', '=', invoice.partner_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('invoice_date', '<', invoice.invoice_date),
        ]
        moves = self.env['account.move'].search(domain)
        return sum(m.amount_total_signed for m in moves)

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        previous_balance_map = {doc.id: self._get_previous_balance(doc) for doc in docs}
        return {
            'docs': docs,
            'previous_balance_map': previous_balance_map,
        }