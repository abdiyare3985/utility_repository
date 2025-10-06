from odoo import models, fields

class MeterReadingReportWizard(models.TransientModel):
    _name = 'meter.reading.report.wizard'
    _description = 'Meter Reading Report Wizard'

    period_date = fields.Date(string='Period Date')
    zone_id = fields.Many2one('utility.meter.zone', string='Zone')

    def action_print_report(self):
        domain = []
        if self.zone_id:
            domain.append(('meter_id.zone_id', '=', self.zone_id.id))
        if self.period_date:
            domain.append(('bill_period', '=', self.period_date))
        readings = self.env['meter.reading'].search(domain)
        print(f'Found {len(readings)} readings for report.')
        data = {
            'period': self.period_date,
            'zone': self.zone_id.name if self.zone_id else '',
        }
        return self.env.ref('utility.action_report_meter_reading').report_action(readings, data=data)