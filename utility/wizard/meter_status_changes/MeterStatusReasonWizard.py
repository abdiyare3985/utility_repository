from odoo import models, fields

class MeterStatusReasonWizard(models.TransientModel):
    _name = 'meter.status.reason.wizard'
    _description = 'Reason for Meter Status Change'

    reason = fields.Text(string="Reason", required=True)

    


    def action_confirm(self):
     active_id = self.env.context.get('active_id')
     new_status = self.env.context.get('new_status')
     meter = self.env['utility.meter'].browse(active_id)
     if meter and new_status:
        old_status = meter.meter_status
        # Disable tracking for this write
        meter.with_context(tracking_disable=True).meter_status = new_status
        meter.message_post(
    subject="Meter status changed",
    body=f"Meter status changed from {old_status} to {new_status}.\nReason: {self.reason}"
)
     return {'type': 'ir.actions.act_window_close'}