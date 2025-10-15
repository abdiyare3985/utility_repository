from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    #_rec_names_search=['name', 'meter_id']
    #_rec_name = 'display_name'
    _sql_constraints = [
        ('name_uniq', 'unique(billing_account)', 'billing_account must be unique.')
    ]

   # meter_ids = fields.One2many('utility.meter', 'partner_id', string='Meters')
    meter_id = fields.Many2one('utility.meter', string='Meter', readonly=False)
    billing_account = fields.Char(string='billing account', default='')
    meter_ids = fields.One2many(
    'utility.meter',  # model
    string='Meters',
    compute='_compute_meter_ids',
    store=False
)

    @api.depends('billing_account')
    def _compute_meter_ids(self):
        for partner in self:
            primary_meter = partner.meter_id.primary_meter if partner.meter_id else None
            if primary_meter:
             partner.meter_ids = self.env['utility.meter'].search([
                ('primary_meter', '=', primary_meter)
            ])


    display_name = fields.Char(
        string='Display Name',
       # compute='_compute_display_name',
        #store=True,
        index=True
    )


    # def name_get(self):
    #     result = []
    #     for partner in self:
    #         name = partner.name or ''
    #         phone = partner.phone or ''
    #         meter = partner.meter_id.name or ''
    #         display = name
    #         if phone:
    #             display += f" ({phone})"
    #         if meter:
    #             display += f" [{meter}]"
    #         result.append((partner.id, display))
    #     return result
    
    
    
    def _compute_display_name(self):
        for rec in self:
            if rec.customer_rank > 0:
               rec.display_name = f"{rec.name} [{rec.billing_account}]"
            else:
               rec.display_name = rec.name


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
     args = list(args or [])
     if name:
        args += ['|', ('name', operator, name), ('meter_id.name', operator, name)]
     return self._search(args, limit=limit, access_rights_uid=name_get_uid, order=order)
    

    # @api.model
    # def get_meters_by_primary_meter(self, primary_meter_value):
    #     """
    #     Returns a recordset of utility.meter records matching the given primary_meter value.
    #     """
    #     return self.env['utility.meter'].search([('primary_meter', '=', primary_meter_value)])
    

  

   
    def hello(self):
       print("Hello from ResPartner")
       pass