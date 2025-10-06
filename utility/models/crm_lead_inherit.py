from odoo import models, fields

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    meter_id = fields.Many2one('utility.meter', string='Meter')
    zone_id = fields.Many2one('utility.meter.zone', string='Zone')
    address = fields.Char(string='Meter Address')

    def action_open_create_customer_meter_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.customer.meter.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_customer_name': self.name if self else False,
                'default_phone': self.phone if self.phone else False,
                'default_email': self.email_from if self.email_from else False,
                'default_zone_id': self.zone_id.id if self.zone_id else False,
                'default_address': self.address or '',
            }
        }
        # print("Action to open create customer meter wizard")
        # pass