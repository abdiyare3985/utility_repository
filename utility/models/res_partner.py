from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    #_rec_names_search=['name', 'meter_id']
    #_rec_name = 'display_name'

    #meter_ids = fields.One2many('utility.meter', 'partner_id', string='Meters')
    meter_id = fields.Many2one('utility.meter', string='Meter', readonly=True)
    upload_id = fields.Integer(string='Upload ID', default=0)
    # meter_name = fields.Char(related='meter_id.name', string='Meter Name', store=True, readonly=True)
    # meter_status = fields.Selection(related='meter_id.meter_status', string='Meter Status', store=False, readonly=True)
    # installation_date = fields.Date(related='meter_id.installation_date', string='Installation Date', store=False, readonly=True)
    # meter_type = fields.Selection(related='meter_id.meter_type', string='Meter Type', store=False, readonly=True)
#     meter_reading_ids = fields.One2many(
#     'meter.reading', 'meter_id',
#     string='Meter Readings',
#     compute='_compute_meter_reading_ids',
#     store=False
# )

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
            rec.display_name = f"{rec.name} [{rec.meter_id.name}]"


    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
     args = list(args or [])
     if name:
        args += ['|', ('name', operator, name), ('meter_id.name', operator, name)]
     return self._search(args, limit=limit, access_rights_uid=name_get_uid, order=order)
    

  

   
    def hello(self):
       print("Hello from ResPartner")
       pass