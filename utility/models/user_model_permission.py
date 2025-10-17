from odoo import api, fields, models

class UserModelPermission(models.Model):
    _name = 'user.model.permission'
    _description = 'User per-model permission helper'
    user_id = fields.Many2one('res.users', required=True, ondelete='cascade')
    model_name = fields.Char(required=True)  # e.g. 'utility.meter'
    name = fields.Char(compute='_compute_name')
    perm_read = fields.Boolean('Read')
    perm_write = fields.Boolean('Write')
    perm_create = fields.Boolean('Create')
    perm_unlink = fields.Boolean('Unlink')

    @api.depends('model_name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.model_name

    def _group_xml_id(self, model_name, perm):
        # create consistent naming: e.g. 'utility.group_meter_read'
        # adapt prefix/module name to your module: 'utility'
        module = 'utility'
        model_key = model_name.replace('.', '_')
        return '%s.group_%s_%s' % (module, model_key, perm)

class ResUsers(models.Model):
    _inherit = 'res.users'

    model_permission_ids = fields.One2many('user.model.permission', 'user_id', string='Model permissions')

    def _apply_model_permission(self, perms):
        """ perms: dict model_name -> {perm: bool,...}
            This method assigns/removes groups based on desired booleans.
        """
        for user in self:
            for model_name, flags in perms.items():
                for perm, flag in flags.items():
                    xmlid = UserModelPermission._group_xml_id(None, model_name, perm) if False else None
            # we'll implement by reading user.model.permission records below

    @api.model
    def _toggle_group_for_user(self, user, model_name, perm, enable):
        # build xml id using same convention as security file
        module = 'utility'
        model_key = model_name.replace('.', '_')
        xmlid = '%s.group_%s_%s' % (module, model_key, perm)
        try:
            group = self.env.ref(xmlid)
        except ValueError:
            group = None
        if not group:
            return
        if enable:
            user.write({'groups_id': [(4, group.id)]})
        else:
            user.write({'groups_id': [(3, group.id)]})

    @api.model
    def update_groups_from_permissions(self, user):
        """Call this after saving permissions rows for `user`."""
        perms = {}
        for rec in user.model_permission_ids:
            perms.setdefault(rec.model_name, {})
            perms[rec.model_name].update({
                'read': rec.perm_read,
                'write': rec.perm_write,
                'create': rec.perm_create,
                'unlink': rec.perm_unlink,
            })
        # apply
        for model_name, flags in perms.items():
            for perm, flag in flags.items():
                self._toggle_group_for_user(user, model_name, perm, flag)

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        for u in users:
            # ensure initial sync
            self.update_groups_from_permissions(u)
        return users

    def write(self, vals):
        res = super().write(vals)
        # after write, resync for affected users
        for u in self:
            self.update_groups_from_permissions(u)
        return res