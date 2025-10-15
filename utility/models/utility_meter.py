from odoo import models, fields, api
from odoo.exceptions import ValidationError

class UtilityMeter(models.Model):
    _name = 'utility.meter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Utility Meter'

    # _sql_constraints = [
    #     ('name_uniq', 'unique(name)', 'Meter Code must be unique.')
    # ]

    _sql_constraints = [
    ('name_uniq', 'unique(name)', 'Meter Code must be unique.'),
    ('customer_id_uniq', 'unique(customer_id)', 'Each customer can only have one meter assigned!'),
]

    _indexes = {
    'utility_meter_customer_id_idx': ('customer_id',),
    'utility_meter_meter_status_idx': ('meter_status',),
    'utility_meter_meter_type_idx': ('meter_type',),
    'utility_meter_zone_id_idx': ('zone_id',),
    'utility_meter_serial_id_idx': ('serial_id',),
}

    name = fields.Integer(string='Meter Code', required=True)
    
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade', domain=[('customer_rank', '>', 0)])
    meter_status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
    ], string='Meter Status', required=True,  default='connected', tracking=True)
    installation_date = fields.Datetime(string='Installation Date')
    # Add other fields as needed
    primary_meter = fields.Integer(string='Primary Meter', default=0)
    meter_type = fields.Selection([
        ('electricity', 'Electricity'),
        ('water', 'Water'),
        ('gas', 'Gas'),
    ], string='Meter Type', required=True)
    house_number = fields.Char(string='House Number')
    street = fields.Char(string='Street')
    area = fields.Char(string='Area')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    address = fields.Char(string='Full Address', compute='_compute_full_address')

    tariff_id = fields.Many2one(
        'product.template',
        domain="[('is_billing_plan', '=', True)]",
        string='Tariff Plan',
        required=True,
        tracking=True,
        help="Pricing plan applied to this meter"
    )
    discount_id = fields.Many2one('meter.discounts', string='Discount')
    serial_id = fields.Many2one('meter.serials', string='Meter Serial')
    zone_id = fields.Many2one('utility.meter.zone', string='Zone')
    group_id = fields.Many2one('meter.groups', string='Meter Group')

    @api.depends('house_number', 'street', 'area', 'city', 'state')
    def _compute_full_address(self):
        for meter in self:
            parts = [meter.house_number, meter.street, meter.area, meter.city, meter.state]
            meter.address = ', '.join(filter(None, parts))



    @api.constrains('customer_id')
    def _check_customer_id(self):
        for meter in self:
            if not meter.customer_id:
                raise ValidationError(_("Each meter must have a customer assigned. Please select a customer."))

    @api.model
    def create(self, vals):
     # If primary_meter is not set, use the value of name (if present)
     if not vals.get('primary_meter') and vals.get('name'):
        vals['primary_meter'] = vals['name']
     meter = super().create(vals)
     if meter.customer_id:
        meter.customer_id.meter_id = meter.id
     return meter

    # def write(self, vals):
    #     res = super().write(vals)
    #     for meter in self:
    #         if meter.customer_id:
    #             meter.customer_id.meter_id = meter.id
    #     return res
    
    def action_disconnect(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason for Disconnection',
            'res_model': 'meter.status.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'active_model': self._name, 'new_status': 'disconnected'},
        }

    def action_connect(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason for Connection',
            'res_model': 'meter.status.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id, 'active_model': self._name, 'new_status': 'connected'},
        }


    # def write(self, vals):
    #     # remember old status per record
    #     old_status = {m.id: m.meter_status for m in self}
    #     res = super().write(vals)
    #     # post a message for any record whose meter_status changed
    #     for rec in self:
    #         old = old_status.get(rec.id)
    #         if old is not None and rec.meter_status != old:
    #             rec.message_post(
    #                 subject="Meter status changed",
    #                 body=f"Meter status changed from <b>{old}</b> to <b>{rec.meter_status}</b> by {self.env.user.name}"
    #             )
    #     return res

    # @api.model
    # def get_by_primary_meter(self, primary_meter_value):
    #     """
    #     Returns a recordset of utility.meter records matching the given primary_meter value.
    #     """
    #     return self.search([('primary_meter', '=', primary_meter_value)])