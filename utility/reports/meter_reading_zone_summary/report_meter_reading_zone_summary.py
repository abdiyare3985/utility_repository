from odoo import models

class ReportMeterReading(models.AbstractModel):
    _name = 'report.utility.report_meter_reading_zone_summary_document'
    _description = 'Meter Reading Constant Report'


    def _get_report_values(self, docids, data=None):
     startDate = data.get('startDate') if data else ''
     endDate = data.get('endDate') if data else ''
     min_consumption = data.get('min_consumption')
     max_consumption = data.get('max_consumption')
     domain = []
     if data:
        if startDate:
            domain.append(('bill_period', '>=', startDate))
        if endDate:
            domain.append(('bill_period', '<=', endDate))
        if min_consumption is not None and max_consumption is not None and min_consumption > max_consumption:
            domain.append(('consumption', '>=', min_consumption))
        if max_consumption is not None and max_consumption > 0:
            domain.append(('consumption', '<=', max_consumption))
     readings = self.env['meter.reading'].search(domain)
 
    # Group readings by zone
     summary = {}
     for reading in readings:
        zone = reading.meter_id.zone_id
        if not zone:
            continue
        if zone.id not in summary:
            summary[zone.id] = {
                'zone': zone,
                'total_consumption': 0.0,
                'total_amount': 0.0,
                'total_fixed': 0.0,
                'total_tax': 0.0,
                'total_total': 0.0,
                'count': 0,
            }
        summary[zone.id]['total_consumption'] += reading.consumption or 0.0
        summary[zone.id]['total_amount'] += reading.amount or 0.0
        summary[zone.id]['total_fixed'] += reading.fixed_charge or 0.0
        summary[zone.id]['total_tax'] += reading.tax_amount or 0.0
        summary[zone.id]['total_total'] += reading.total_amount or 0.0
        summary[zone.id]['count'] += 1

    # Convert summary to a list for easy iteration in QWeb
     summary_list = list(summary.values())

     return {
        'summary': summary_list,
        'startDate': startDate,
        'endDate': endDate,
        'min_consumption': min_consumption,
        'max_consumption': max_consumption,
    }