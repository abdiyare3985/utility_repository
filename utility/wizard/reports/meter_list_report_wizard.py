from odoo import models, fields

class MeterListReportWizard(models.TransientModel):
    _name = 'meter.list.report.wizard'
    _description = 'Meter List Report Wizard'

    # Add any filter fields you want, e.g.:
    zone_id = fields.Many2one('utility.meter.zone', string='Zone')

    # def action_print_report(self):
    #     domain = []
    #     if self.zone_id:
    #         domain.append(('zone_id', '=', self.zone_id.id))
    #     meters = self.env['utility.meter'].search(domain)
    #     # This will trigger the PDF report and Odoo will handle the download/open
    #     return self.env.ref('utility.action_report_utility_meter_list').report_action(meters)

    def action_print_report(self):
        # Collect domain/filters if needed
        domain = []
        if self.zone_id:
            domain.append(('zone_id', '=', self.zone_id.id))
   #    meters = self.env['utility.meter'].search(domain)
        meters = self.env['utility.meter'].search(domain, order='name')
        return self.env.ref('utility.action_report_utility_meter_list').report_action(meters)