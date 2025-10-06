from odoo import models, fields, api, _
class SahalImportPaymentLine(models.Model):
    _name = 'sahal.import.payment.line'
    _description = 'Sahal Import Payment Line'

    sahal_import_id = fields.Many2one('sahal.import', string='Sahal Import', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    amount = fields.Float(string='Amount', required=True)