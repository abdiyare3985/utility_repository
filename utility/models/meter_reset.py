from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MeterReset(models.Model):
    _name = 'meter.reset'
    _description = 'Meter Reset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
    ('unique_meter', 'unique(meter_id)', 'Each meter can only have one reset record!')
]

    meter_id = fields.Many2one('utility.meter', string='Meter', required=True)
    #previous_reading = fields.Float(string='Previous Reading', required=True)
    current_reading = fields.Float(string='Current Reading', required=True)
    reset_date = fields.Date(string='Reset Date', default=fields.Date.context_today, required=True)
    note = fields.Text(string='Reason/Note')
    meter_reset_type = fields.Selection([
    ('reset', 'Reset'),
    ('reading', 'reading')
], string='Reset Type', required=True, default='reset')

    @api.model
    def create(self, vals):
     record = super().create(vals)
     if vals.get('meter_reset_type') == 'reset':
        self.env['meter.reset.history'].create({
            'meter_id': record.meter_id.id,
            'current_reading': record.current_reading,
            'reset_date': record.reset_date,
            'note': record.note,
            'meter_reset_type': record.meter_reset_type,
        })
     return record

    def write(self, vals):
     res = super().write(vals)
     for rec in self:
        if vals.get('meter_reset_type', rec.meter_reset_type) == 'reset':
            self.env['meter.reset.history'].create({
                'meter_id': rec.meter_id.id,
                'current_reading': rec.current_reading,
                'reset_date': rec.reset_date,
                'note': rec.note,
                'meter_reset_type': rec.meter_reset_type,
            })
     return res