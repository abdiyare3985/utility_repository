from odoo import models

class ReportMeterReading(models.AbstractModel):
    _name = 'report.utility.report_meter_reading_pending_document'
    _description = 'Meter Reading Pending Report'


    def _get_report_values(self, docids, data=None):
        print('Generating Meter Reading Report...', data)
        # docs = self.env['meter.reading'].browse(docids)
        # print(f'Generating report for {len(docs)} readings.')
        # domain = []
        # if self.zone_id:
        #     domain.append(('meter_id.zone_id', '=', self.zone_id.id))
        # if self.period_date:
        #     domain.append(('bill_period', '=', self.period_date))
        # readings = self.env['meter.reading'].search(domain)
        # period = data.get('period') if data else ''
        # zone = data.get('zone') if data else ''
        # print(f'Report parameters - Period: {period}, Zone: {zone}')
        # return {
        #     'docs': docids,
        #     'period': period,
        #     'zone': zone,
        # }
        print('XXXXXXXXXXXXXXXXXXXXXPENDING>>>>>>>>>>>>>>>>>>>>>>')
        startDate = data.get('startDate') if data else ''
        endDate = data.get('endDate') if data else ''
        zone = data.get('zone') if data else ''
        domain = []
        # if data:
           #if data.get('zone'):
                #zone = self.env['utility.meter.zone'].search([('name', '=', data['zone'])], limit=1)
        if zone:
           zone_rec = self.env['utility.meter.zone'].search([('name', '=', zone)], limit=1)
           if zone_rec:
            domain.append(('zone_id', '=', zone_rec.id))
    # 1. Get all meters in the selected zone
        meters = self.env['utility.meter'].search(domain)
        print('Meters in zone:', meters)

    # 2. Get all readings for the selected period and zone
        reading_domain = []
        # if period:
        #    reading_domain.append(('bill_period', '=', period))
        if startDate:
               domain.append(('bill_period', '>=', startDate))
        if endDate:
               domain.append(('bill_period', '<=', endDate))
        if zone:
         reading_domain.append(('meter_id.zone_id', '=', zone_rec.id))
        readings = self.env['meter.reading'].search(reading_domain)
        print('Readings for period and zone:', readings)

    # 3. Get meter IDs that already have readings for that period
        meters_with_readings = readings.mapped('meter_id').ids

    # 4. Filter meters that do NOT have readings for that period
        pending_meters = meters.filtered(lambda m: m.id not in meters_with_readings)
        print('Pending meters:', pending_meters)

        # prev_readings = {}
        # for meter in pending_meters:
        #     last_reset = self.env['meter.reset'].search(
        #      [('meter_id', '=', meter.id)],
        #      order='reset_date desc', limit=1
        # )
        # prev_readings[meter.id] = last_reset.current_reading if last_reset else 0.0

        return {
        'docs': pending_meters,
        'StartDate': startDate,
        'EndDate': endDate,
        'zone': zone,
        #'prev_readings': prev_readings,
    }


   