from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    is_technitian = fields.Boolean(string="Is Technician")
    is_meterreader = fields.Boolean(string="Is Meter Reader")
    # utility_group_id = fields.Many2one(
    #     'res.groups',
    #     string="Utility Group",
    #     domain="[('category_id', '=', ref('utility.module_category_utilities'))]",
    #     help="Select one utility-related group."
    # )

    # utility_group_id = fields.Many2one(
    #     'res.groups',
    #     string="Utility Group",
    #     # Do not use ref() directly here:
    #     domain="[('category_id', '=', context.get('module_category_utilities'))]",
    #     help="Select one utility-related group."
    # )