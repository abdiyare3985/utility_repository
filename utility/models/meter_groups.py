from odoo import models, fields, api

class MeterGroup(models.Model):
    _name = 'meter.groups'
    _description = 'Meter Group'
    _sql_constraints = [
    ('code_unique', 'unique(code)', 'Group Code must be unique!'),
]
    
    name = fields.Char(string='Group Name', required=True)
    code = fields.Char(string='Group Code', required=True)
    description = fields.Text(string='Description')

    # meter_ids = fields.One2many('utility.meter', 'group_id', string='Meters')