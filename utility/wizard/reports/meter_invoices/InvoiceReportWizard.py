from odoo import models, fields,api

class InvoiceReportWizard(models.TransientModel):
    _name = 'invoice.report.wizard'
    _description = 'Invoice Report Wizard'

    invoice_ids = fields.Many2many('account.move', string='Invoices', domain=[('move_type', '=', 'out_invoice')])
    invoice_meter_info = fields.Char(string='Invoice/Meter Info', compute='_compute_invoice_meter_info')

    @api.depends('invoice_ids')
    def _compute_invoice_meter_info(self):
        for wizard in self:
            infos = []
            for inv in wizard.invoice_ids:
                meter_name = inv.meter_reading_id.meter_id.name if inv.meter_reading_id else ''
                infos.append(f"{inv.name} / {meter_name}")
            wizard.invoice_meter_info = ', '.join(infos)

    def action_print_report(self):
        # Return the report action for selected invoices
        return self.env.ref('utility.action_report_custom_invoice').report_action(self.invoice_ids)