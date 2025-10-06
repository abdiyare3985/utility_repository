from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class MeterSerials(models.Model):
    _name = 'meter.serials'
    _description = 'Meter Serial Number Registry'
    _order = 'serial_number'
    _rec_name = "serial_number"
    _sql_constraints = [
        ('serial_unique', 'UNIQUE(serial_number)', 'This serial number is already registered!'),
    ]

    serial_number = fields.Char(
        string='Serial Number',
        required=True,
        index=True,
        tracking=True,
        help="Unique manufacturer identifier (alphanumeric, min 3 chars)"
    )
    

    meter_type = fields.Selection([('mechanical', 'Mechanical'), ('digital', 'Digital')], string='Meter Type')
    model = fields.Char(string='Model')
    capacity = fields.Float(string='Capacity')
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([('available', 'Available'), ('assigned', 'Assigned'), ('retired', 'Retired')], compute='_compute_state', store=True, string='State')
    assigned_date = fields.Date(string='Assigned Date')
    retired_date = fields.Date(string='Retired Date')

    initial_reading = fields.Float(string='Initial Reading', help="Factory or installation starting value")
    last_reading = fields.Float(string='Last Reading', help="Last recorded reading for this meter")

    
    @api.depends('assigned_date', 'retired_date')
    def _compute_state(self):
        for rec in self:
            if rec.retired_date:
                rec.state = 'retired'
            elif rec.assigned_date:
                rec.state = 'assigned'
            else:
                rec.state = 'available'
    

    @api.constrains('serial_number')
    def _check_serial_number_length(self):
        for rec in self:
            if rec.serial_number and len(rec.serial_number) < 3:
                raise ValidationError(_("Serial number must be at least 3 characters long."))