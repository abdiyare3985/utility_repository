from odoo import models

class ReportMeterReading(models.AbstractModel):
    _name = 'report.utility.report_meter_reading_document'
    _description = 'Meter Reading Report'


    def _get_report_values(self, docids, data=None):
        print('Generating Meter Reading Report...', data)


        startDate = data.get('startDate') if data else ''
        endDate = data.get('endDate') if data else ''
        zone = data.get('zone') if data else ''
        min_consumption = data.get('min_consumption')
        max_consumption = data.get('max_consumption')
        domain = []
        if data:
            if data.get('zone'):
                zone = self.env['utility.meter.zone'].search([('name', '=', data['zone'])], limit=1)
                if zone:
                    domain.append(('meter_id.zone_id', '=', zone.id))
            # if data.get('period'):
            #     domain.append(('bill_period', '=', data['period']))
            if startDate:
               domain.append(('bill_period', '>=', startDate))
            if endDate:
               domain.append(('bill_period', '<=', endDate))
            if min_consumption is not None and max_consumption is not None and max_consumption > 0:
               domain.append(('consumption', '>=', min_consumption))
            if max_consumption is not None and max_consumption > 0:
               domain.append(('consumption', '<=', max_consumption))
        readings = self.env['meter.reading'].search(domain)

        return {
        'docs': readings,
        'startDate': startDate,
        'endDate': endDate,
        'zone': data.get('zone') if data else '',
        'min_consumption': min_consumption,
        'max_consumption': max_consumption,
    }


   