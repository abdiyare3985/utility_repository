from odoo import models, fields

class MeterReadingReportWizard(models.TransientModel):
    _name = 'meter.reading.report.wizard'
    _description = 'Meter Reading Report Wizard'

    period_date = fields.Date(string="Start Date", required=True)
    period_date2 = fields.Date(string="End Date", required=True)
    zone_id = fields.Many2one('utility.meter.zone', string='Zone')
    status = fields.Selection([
        ('billed', 'Billed'),
        ('unbilled', 'Unbilled')
    ], string='Status', default = 'billed')
    min_consumption = fields.Float(string='Min Consumption')
    max_consumption = fields.Float(string='Max Consumption')

    def action_print_report(self):
        domain = []
        if self.zone_id:
            domain.append(('meter_id.zone_id', '=', self.zone_id.id))
        if self.period_date:
            domain.append(('bill_period', '=', self.period_date))
        readings = self.env['meter.reading'].search(domain)
        print('meter readings for report:', readings.ids)
        print('meter readings for report:', readings)
        print(f'Found {len(readings)} readings for report.')
        data = {
            'startDate': self.period_date,
            'endDate': self.period_date2,
            'zone': self.zone_id.name if self.zone_id else '',
            'min_consumption': self.min_consumption,
            'max_consumption': self.max_consumption,
        }
        return self.env.ref('utility.action_report_meter_reading').report_action([], data=data)
    
    def action_print_pending_report(self):
        domain = []
        if self.zone_id:
            domain.append(('meter_id.zone_id', '=', self.zone_id.id))
        if self.period_date:
            domain.append(('bill_period', '=', self.period_date))
        readings = self.env['meter.reading'].search(domain)
        print('meter readings for report:', readings.ids)
        print('meter readings for report:', readings)
        print(f'Found {len(readings)} readings for report.')
        data = {
            'startDate': self.period_date,
            'endDate': self.period_date2,
            'zone': self.zone_id.name if self.zone_id else '',
        }
        return self.env.ref('utility.action_report_meter_reading_pending').report_action([], data=data)
    
    def action_print_constant_report(self):
        domain = []
        if self.zone_id:
            domain.append(('meter_id.zone_id', '=', self.zone_id.id))
        if self.period_date:
            domain.append(('bill_period', '=', self.period_date))
        readings = self.env['meter.reading'].search(domain)
        print('meter readings for report:', readings.ids)
        print('meter readings for report:', readings)
        print(f'Found {len(readings)} readings for report.')
        data = {
            'startDate': self.period_date,
            'endDate': self.period_date2,
            'zone': self.zone_id.name if self.zone_id else '',
            'min_consumption': self.min_consumption,
            'max_consumption': self.max_consumption,
        }
        return self.env.ref('utility.action_report_meter_reading_zone_summary').report_action([], data=data)