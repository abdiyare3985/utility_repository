from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
class CreateCustomerMeterWizard(models.TransientModel):
    _name = 'create.customer.meter.wizard'
    _description = 'Create Customer Meter Wizard'

    lead_id = fields.Many2one('crm.lead', string="Opportunity", required=True)
    customer_name = fields.Char(string='Customer Name', required=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    primary_meter = fields.Integer(string='Primary Meter', default=0)
    existing_customer = fields.Boolean(string="Link to Existing Customer")
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        domain="[('customer_rank', '>', 0)]",  # Only customers
        
    )


    name = fields.Char(
        string='Meter ID',
        
        index=True,
        #tracking=True,
        #default=lambda self: self.env['ir.sequence'].next_by_code('water.meter'),
        help="Unique meter identification number"
    )
    
    # serial_id = fields.Many2one(
    #     'meter.serial',
    #     string='Serial Number',
    #     required=True,
    #     domain="[('state','=','available')]",
    #    # ondelete='restrict',
    #     #tracking=True
    # )


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
    @api.depends('house_number', 'street', 'area', 'city', 'state')
    def _compute_full_address(self):
        for meter in self:
            parts = [meter.house_number, meter.street, meter.area, meter.city, meter.state]
            meter.address = ', '.join(filter(None, parts))

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
    
    # group_id = fields.Many2one(
    #     'meter.group',
    #     string='Technical Group',
    #     #tracking=True,
    #     help="Functional grouping of meters"
    # )
    
    # coordinates = fields.Char(
    #     string='GPS Coordinates',
    #     #tracking=True,
    #     help="Latitude,Longitude (e.g. '12.345,-12.345')"
    # )
    
    # latitude = fields.Float(
    #     string='Latitude',
    #     digits=(10, 7),
    #     compute='_compute_lat_lng',
    #     store=True
    # )
    
    # longitude = fields.Float(
    #     string='Longitude',
    #     digits=(10, 7),
    #     compute='_compute_lat_lng',
    #     store=True
    # )
    
    # house_number = fields.Char(
    #     string='House Number',
    #     #tracking=True,
    #     size=16
    # )
    
    # street = fields.Char(
    #     string='Street',
    #     #tracking=True
    # )
    
    # area = fields.Char(
    #     string='Area/Neighborhood',
    #     #tracking=True
    # )

    # ========== SERVICE FIELDS ==========
    connection_date = fields.Date(
        string='Connection Date',
        default=fields.Date.today,
        required=True,
        #tracking=True
    )
    
    status = fields.Selection(
        [('connected', 'Connected'),
         ('disconnected', 'Disconnected'),
         ('blocked', 'Blocked')],
        string='Connection Status',
        default='connected',
        #tracking=True,
        index=True
    )
    
    # tariff_id = fields.Many2one(
    #     'product.template',
    #     domain="[('is_billing_plan', '=', True)]",
    #     string='Tariff Plan',
    #     required=True,
    #     #tracking=True,
    #     help="Pricing plan applied to this meter"
    # )
    
    # discount_id = fields.Many2one(
    #     'meter.discount',
    #     string='Discount',
    #     #tracking=True,
    #     #domain="[('active','=',True)]"
    # )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        lead = self.env['crm.lead'].browse(active_id)
        if lead.partner_id:
            res['partner_id'] = lead.partner_id.id
        return res
    

    
        

    def action_create_meter(self):
        try:
            with self.env.cr.savepoint():
                customer = self.env['res.partner'].create({
                    'name': self.customer_name,
                    'phone': self.phone,
                    'email': self.email,
                    'customer_rank': 100
                })
                last_meter = self.env['utility.meter'].search([], order='name desc', limit=1)
                if last_meter and last_meter.name:
                    new_id = int(last_meter.name) + 1
                else:
                    new_id = 1

                if self.existing_customer and self.partner_id:
                    primary_id = self.partner_id.meter_id.primary_meter if self.partner_id.meter_id else 0
                else:
                    primary_id = new_id

                meter = self.env['utility.meter'].create({
                    'name': new_id,
                    'serial_id': self.serial_id.id if self.serial_id else False,
                    'customer_id': customer.id,
                    'primary_meter': primary_id,
                    'zone_id': self.zone_id.id if self.zone_id else False,
                    'group_id': self.group_id.id if self.group_id else False,
                    'house_number': self.house_number,
                    'street': self.street,
                    'area': self.area,
                    'city': self.city,
                    'state': self.state,
                    'installation_date': self.connection_date,
                    'meter_status': self.status,
                    'tariff_id': self.tariff_id.id if self.tariff_id else False,
                    'discount_id': self.discount_id.id if self.discount_id else False,
                    'meter_type': self.meter_type,
                })
                customer.meter_id = meter.id
                self.lead_id.partner_id = customer.id
                self.lead_id.meter_id = meter.id
                customer.billing_account = new_id
        except Exception as e:
            raise ValidationError(_("Failed to create customer and meter: %s") % str(e))
        return {'type': 'ir.actions.act_window_close'}
    

    @api.onchange('existing_customer')
    def _onchange_existing_customer(self):
        if not self.existing_customer:
            self.partner_id = False