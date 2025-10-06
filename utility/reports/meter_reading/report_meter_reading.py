from odoo import models

class ReportMeterReading(models.AbstractModel):
    _name = 'report.utility.report_meter_reading_document'
    _description = 'Meter Reading Report'


    def _get_report_values(self, docids, data=None):
        docs = self.env['meter.reading'].browse(docids)
        print(f'Generating report for {len(docs)} readings.')
        period = data.get('period') if data else ''
        zone = data.get('zone') if data else ''
        print(f'Report parameters - Period: {period}, Zone: {zone}')
        return {
            'docs': docs,
            'period': period,
            'zone': zone,
        }


   