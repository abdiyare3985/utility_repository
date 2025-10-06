from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MeterDiscounts(models.Model):
    _name = 'meter.discounts'
    _description = 'Water Meter Discount'
    _order = 'name'
    _sql_constraints = [
    ('name_unique', 'unique(name)', 'Discount name must be unique!'),
    ]
    
    name = fields.Char(
        string='Discount Name',
        required=True,
        help="Descriptive name for this discount (e.g., Business, Bulk Discount)"
    )
    
    percentage = fields.Float(
        string='Discount Percentage',
        required=True,
        digits=(5, 2),  # Allows for 100.00% max with 2 decimal places
        help="Percentage discount to apply (e.g., 10.5 for 10.5% discount)",
        default=0.0
    )
    
  
    description = fields.Text(
        string='Description',
        help="Detailed explanation of discount terms and conditions"
    )
    active = fields.Boolean(default=True)
    usage_type = fields.Selection([
    ('bulk', 'Bulk'),
    ('promo', 'Promotional'),
    ('seasonal', 'Seasonal'),
    ], string='Usage Type')

    
    @api.constrains('percentage')
    def _check_percentage(self):
     for rec in self:
        if rec.percentage < 0 or rec.percentage > 100:
            raise ValidationError(_("Discount percentage must be between 0 and 100."))