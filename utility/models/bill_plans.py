from odoo import models, fields, api

class BillPlans(models.Model):
    _inherit = 'product.template'
    
    is_billing_plan = fields.Boolean(
        string='Billing Plan',
        help="Check this if the product is used as a tariff for water services",
        default=False,
        tracking=True
    )
    
    # Optional: Add domain to show only billing plans in certain selections
    def _default_is_billing_plan(self):
        return self.env.context.get('default_is_billing_plan', False)
    

    fixed_charge = fields.Float(
        string='Fixed Charge',
        digits=(12, 2),
        default=0.0,
        help="Base fee applied regardless of consumption"
    )
    
    # block_ids = fields.One2many(
    #     'billing.tariff.block',
    #     'product_id',
    #     string='Consumption Blocks',
    #     help="Define tiered pricing blocks"
    # )

    pricing_method = fields.Selection([
        #('block_rate', 'Block Rate'),
        ('consumption_based', 'Consumption Based Rate'), 
        ('range_based', 'Range Based Rate'),
    ], string='Pricing Method', default='Range Based Rate', required=True)
    
    # Add range-based rate table
    range_ids = fields.One2many(
        'billing.tariff.range',
        'product_id',
        string='Consumption Ranges',
        help="Define range-based pricing"
    )
    
    # Consumption based rate fields
    consumption_rate = fields.Float(
        string='Rate per m³',
        digits=(12, 4),
        help="Standard rate per cubic meter for consumption-based pricing"
    )

    tax_on_consumption = fields.Boolean(
        string="Apply Tax to Consumption",
        help="If enabled, taxes will be applied to consumption charges",
        default=True)
    

    def compute_bill(self, consumption):
     print("Computing bill for consumption:", consumption)
     self.ensure_one()
     #total = self.fixed_charge or 0.0
     total = 0.0
     if self.pricing_method == 'block_rate':
        print("Computing bill using block rate method")
        # Block rate: sum up each block's charge
        for block in sorted(self.block_ids, key=lambda b: b.from_qty):
            if consumption > block.from_qty:
                qty = min(consumption, block.to_qty) - block.from_qty + 1
                total += qty * block.price_unit
     elif self.pricing_method == 'consumption_based':
        print(f"Computing bill using consumption based method {self.consumption_rate}")
        #total += consumption * (self.consumption_rate or 0.0)
        total = self.consumption_rate or 0.0
     elif self.pricing_method == 'range_based':
        print("Computing bill using range based method")
        for rng in self.range_ids:
            if rng.min_value <= consumption <= rng.max_value:
                #total += consumption * rng.rate
                total = rng.rate
                break
     return total