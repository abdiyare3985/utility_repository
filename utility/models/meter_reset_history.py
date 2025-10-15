from odoo import models, fields, api, _
class MeterResetHistory(models.Model):
    _name = 'meter.reset.history'
    _description = 'Meter Reset History'

    meter_id = fields.Many2one('utility.meter', string='Meter', required=True)
    meter_name = fields.Integer(related='meter_id.name', string='Meter Name', store=False)
    current_reading = fields.Float(string='Current Reading', required=True)
    reset_date = fields.Date(string='Reset Date', required=True)
    note = fields.Text(string='Reason/Note')
    meter_reset_type = fields.Selection([
        ('reset', 'Reset'),
        ('reading', 'Reading')
    ], string='Reset Type', required=True)