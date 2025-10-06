from odoo import models, fields

class MeterZone(models.Model):
    _name = 'utility.meter.zone'
    _description = 'Meter Zone'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    meter_reader = fields.Many2one(
        'res.users',
        string='Meter Reader',
        domain=[('is_meterreader', '=', True)],
        help='User responsible for collecting meter readings in this zone'
    )