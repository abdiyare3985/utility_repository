from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from calendar import monthrange
from datetime import date, timedelta

class MeterReading(models.Model):
    _name = 'meter.reading'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Meter Reading'
    _order = 'reading_date desc'

    meter_id = fields.Many2one('utility.meter', string='Meter', required=True, ondelete='cascade')
    meter_name = fields.Integer(related='meter_id.name', string='Meter Name', store=True)
    
    customer_id = fields.Many2one(related='meter_id.customer_id', string='Customer', store=True)
    zone_name = fields.Char(related='meter_id.zone_id.name', string='Zone', store=False)
    #reading_date = fields.Date(string='Reading Date', required=True, default=fields.Date.today)
    reading_date = fields.Datetime(string='Reading Date', required=True, default=fields.Datetime.now)
    bill_period = fields.Date(string='Billing Period', compute='_compute_bill_period', store=True)
    previous_reading = fields.Float(string='Previous Reading', readonly=True)
    current_reading = fields.Float(string='Current Reading', required=True)
    consumption = fields.Float(string='Consumption', compute='_compute_consumption', store=True)
    billed = fields.Boolean(string='Billed', default=False)

    discount_amount = fields.Float(string='Discount Amount', readonly=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    rate_used = fields.Float(string='Rate Used', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    fixed_charge = fields.Float(string='Fixed Charge', readonly=True)
    tax_amount = fields.Float(string='Tax Amount', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ],
        string='Invoice State',
        related='invoice_id.state',
        store=True,
        readonly=True
    )
    payment_state = fields.Selection(
        related='invoice_id.payment_state',
        string='Payment State',
        store=False
    )
    is_reset_reading = fields.Boolean(
        string='Is Reset Reading',
        default=False,
        help='Enable this if this reading is a reset (meter changed or reset), not a normal monthly reading.'
    )

    @api.depends('previous_reading', 'current_reading')
    def _compute_consumption(self):
        for rec in self:
            print(f"Computing consumption for record ID {rec.id}: Previous reading = {rec.previous_reading}, Current reading = {rec.current_reading}")
            rec.consumption = rec.current_reading - rec.previous_reading
            print(f"Computed ONE consumption: {rec.consumption}")

    @api.depends('reading_date')
    def _compute_bill_period(self):
        for rec in self:
            if rec.reading_date:
                day = rec.reading_date.day
                if 22 <= day <= 31:
                    year = rec.reading_date.year
                    month = rec.reading_date.month
                else:
                    prev_month_date = rec.reading_date.replace(day=1) - timedelta(days=1)
                    year = prev_month_date.year
                    month = prev_month_date.month
                last_day = monthrange(year, month)[1]
                rec.bill_period = date(year, month, last_day)
            else:
                rec.bill_period = False

    @api.onchange('meter_id', 'reading_date')
    def _onchange_meter_id(self):
        for rec in self:
            if rec.meter_id and rec.reading_date:
                # last_reading = self.env['meter.reading'].search([
                #     ('meter_id', '=', rec.meter_id.id),
                #     ('reading_date', '<', rec.reading_date)
                # ], order='reading_date desc', limit=1)
                last_reading = self.env['meter.reset'].search([
                    ('meter_id', '=', rec.meter_id.id),
                ], order='reset_date desc', limit=1)
                # if last_reading:
                #     rec.previous_reading = last_reading.current_reading
                # elif rec.meter_id.serial_id:
                #     rec.previous_reading = rec.meter_id.serial_id.initial_reading or 0.0
                # else:
                #     rec.previous_reading = 0.0
                if last_reading:
                    rec.previous_reading = last_reading.current_reading
                    print("Found last reset reading:", rec.previous_reading)
            else:
                rec.previous_reading = 0.0
                print("No meter or reading date selected, setting previous reading to 0.0")

    # @api.constrains('current_reading', 'previous_reading')
    # def _check_readings(self):
    #     for rec in self:
    #         if rec.current_reading < rec.previous_reading:
    #             raise ValidationError(_("Current reading cannot be less than previous reading."))

    @api.constrains('current_reading', 'previous_reading')
    def _check_readings(self):
        for rec in self:
            if rec.current_reading < rec.previous_reading:
                raise ValidationError(_("Current reading cannot be less than previous reading."))
            if rec.consumption < 0:
                raise ValidationError(_("Consumption cannot be less than zero."))
            # if rec.current_reading == rec.previous_reading:
            #     raise ValidationError(_("Consumption cannot be zero."))

    _sql_constraints = [
        ('unique_meter_period', 'unique(meter_id,bill_period)', 'A reading for this meter and period already exists!'),
    ]

    # def _generate_bill(self):
    #     for rec in self:
    #         if rec.billed or rec.consumption <= 0:
    #             continue  # Already billed or nothing to bill
    #         tariff = rec.meter_id.tariff_id
    #         if not tariff:
    #             raise ValidationError(_("No tariff plan set for this meter."))
    #         amount = tariff.compute_bill(rec.consumption)
    #         print(f"Billing {rec.customer_id.name} for {rec.consumption} units: {amount}")
    #         # Example: create invoice (account.move)
    #         invoice_line_vals = {
    #             'name': f'Meter Reading for {rec.bill_period}',
    #             'quantity': rec.consumption,
    #             'price_unit': tariff.consumption_rate,
    #             'product_id': tariff.id,
    #         }
    #         invoice_vals = {
    #             'move_type': 'out_invoice',
    #             'partner_id': rec.customer_id.id,
    #             'invoice_date': rec.reading_date,
    #             'invoice_line_ids': [(0, 0, invoice_line_vals)],
    #         }
    #         self.env['account.move'].create(invoice_vals)
    #         rec.billed = True

    # def _generate_bill(self):
    #  for rec in self:
    #     if rec.billed or rec.consumption <= 0:
    #         continue  # Already billed or nothing to bill
    #     tariff = rec.meter_id.tariff_id
    #     if not tariff:
    #         raise ValidationError(_("No tariff plan set for this meter."))
    #     #amount = tariff.compute_bill(rec.consumption)
    #     rate = tariff.compute_bill(rec.consumption)
    #     #print(f"Billing {rec.customer_id.name} for {rec.consumption} units: {amount}")
    #     print(f"Tariff rate: {rate}")

    #     # --- Apply discount if available ---
    #     discount_percent = 0.0
    #     if rec.meter_id.discount_id and rec.meter_id.discount_id.percentage:
    #         print("Applying discount")
    #         discount_percent = rec.meter_id.discount_id.percentage
    #         print(f"Discount percent: {discount_percent}")
    #     print(f"Applying discount of {discount_percent}%")
    #     discount_amount = (rate * rec.consumption) * (discount_percent / 100.0)
    #     print(f"Discount amount: {discount_amount}")
    #     #final_amount = amount - discount_amount
    #     #print(f"Final amount after discount: {final_amount}")


    #     rec.discount_amount = discount_amount  # Store for history

    #     invoice_line_ids = []

    #      # 1. Add consumption line
    #     invoice_line_ids.append((0, 0, {
    #         'name': f'Meter Reading for {rec.bill_period}',
    #         'quantity': rec.consumption,
    #         'price_unit': rate,
    #         #'discount': discount_percent,
    #         'product_id': tariff.id,
    #     }))

    #     # 2. Add fixed charge line if applicable
    #     if tariff.fixed_charge:
    #         invoice_line_ids.append((0, 0, {
    #             'name': _('H.Degmada'),
    #             'quantity': 1,
    #             'price_unit': tariff.fixed_charge,
    #             'product_id': 2,  # Product with ID 1
    #         }))

       

    #     # 3. Add discount line as negative value if discount exists
    #     if discount_amount:
    #         invoice_line_ids.append((0, 0, {
    #             'name': _(f'Discount from {discount_percent}% of {rec.consumption * rate}'),
    #             'quantity': 1,
    #             'price_unit': -discount_amount,
    #             'product_id': 3,
    #         }))

    #     invoice_vals = {
    #         'move_type': 'out_invoice',
    #         'partner_id': rec.customer_id.id,
    #         'invoice_date': rec.reading_date,
    #         'invoice_line_ids': invoice_line_ids,
    #         'meter_reading_id': rec.id,  # Link to meter reading
    #     }
       
    #     invoice = self.env['account.move'].create(invoice_vals)
    #     rec.invoice_id = invoice.id
    #     rec.billed = True
    #     invoice.action_post()  # <-- This will post the invoice

    def _has_open_balance(self, partner):
     #print(f"Checking open balance for partner {partner.name}")
     """Return True if the partner has a positive receivable balance (i.e., owes money)."""
     partner = partner.commercial_partner_id
     #print(f"Partner {partner.name} has credit: {partner.credit}, debit: {partner.debit}, balance: {partner.balance}")
    # This is the total receivable (invoices - payments/credits)
     return partner.credit

    def _generate_billOLD(self):
        partner = self.customer_id.commercial_partner_id
        print(f"Customer OPEN BALANCE {partner.credit} has an open balance. Cannot generate new bill.")
        for rec in self:
            if rec.billed or rec.consumption <= 0:
               continue

           # --- Check for open balance (unpaid invoices minus advances/credits) ---
            if self._has_open_balance(rec.customer_id):
             
             raise ValidationError(_("This customer has an outstanding balance. Please settle open balances before generating a new bill."))
            pass


    def _generate_bill(self):
     DISCOUNT_PRODUCT_ID = 3  # Replace with your actual discount product ID
     FIXED_CHARGE_PRODUCT_ID = 2  # Replace with your actual fixed charge product ID
     print(f"Previous reading: {self.previous_reading}, Current reading: {self.current_reading}")
     consumption = self.current_reading - self.previous_reading
     self.consumption = consumption if consumption >= 0 else 0
     print(f"Computed consumption: {self.consumption}")
     for rec in self:
        if rec.billed or rec.consumption <= 0:
            continue
        tariff = rec.meter_id.tariff_id
        if not tariff:
            raise ValidationError(_("No tariff plan set for this meter."))

        print("Consumption being passed to compute_bill:", rec.consumption)
        rate = tariff.compute_bill(rec.consumption)
        print(f"Tariff rate: {rate}")
        rec.rate_used = rate
        
        if rate == 0.0 and tariff.default_rate > 0.0:
            amount = tariff.default_rate
            rec.amount = amount
            discount_amount = 0
            rec.discount_amount = discount_amount
            rate= amount
            consumption = 1
           # rec.rate_used = tariff.default_rate

        else:    
         amount = rate * rec.consumption
         rec.amount = amount

         discount_percent = 0.0
         if rec.meter_id.discount_id and rec.meter_id.discount_id.percentage:
            discount_percent = rec.meter_id.discount_id.percentage
         discount_amount = amount * (discount_percent / 100.0)
         rec.discount_amount = discount_amount

        invoice_line_ids = []

        # 1. Add consumption line
        invoice_line_ids.append((0, 0, {
            'name': f'Meter Reading for {rec.bill_period}',
            'quantity': consumption,
            'price_unit': rate,
            'product_id': tariff.id,
        }))

        # 2. Add fixed charge line if applicable
        if tariff.fixed_charge:
            invoice_line_ids.append((0, 0, {
                'name': _('Fixed Charge'),
                'quantity': 1,
                'price_unit': tariff.fixed_charge,
                'product_id': FIXED_CHARGE_PRODUCT_ID,
            }))
            rec.fixed_charge = tariff.fixed_charge
        else:
            rec.fixed_charge = 0.0

        # 3. Add discount line as negative value if discount exists
        if discount_amount:
            invoice_line_ids.append((0, 0, {
                'name': _(f'Discount from {discount_percent}% of {amount}'),
                'quantity': 1,
                'price_unit': -discount_amount,
                'product_id': DISCOUNT_PRODUCT_ID,
            }))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': rec.customer_id.id,
            'invoice_date': rec.reading_date,
            'invoice_line_ids': invoice_line_ids,
            'meter_reading_id': rec.id,
            'invoice_origin': (
        f"Bill Period: {rec.bill_period or ''} / "
        f"{rec.current_reading or 0} - {rec.previous_reading or 0} = {rec.consumption or 0}"
    ),
        }

        invoice = self.env['account.move'].create(invoice_vals)
        rec.invoice_id = invoice.id
        rec.billed = True

        # Compute and store tax amount
        rec.tax_amount = sum(line.tax_ids.compute_all(line.price_unit, rec.customer_id.property_account_position_id, line.quantity)['taxes'][0]['amount']
                             for line in invoice.invoice_line_ids if line.tax_ids)

        invoice.action_post()

        rec.total_amount = (rec.amount or 0.0) + (rec.fixed_charge or 0.0) - (rec.discount_amount or 0.0) + (rec.tax_amount or 0.0)

    # @api.model
    # def create(self, vals):
    #     # Set previous_reading before creation
    #     if vals.get('meter_id') and vals.get('reading_date'):
    #         last_reading = self.env['meter.reading'].search([
    #             ('meter_id', '=', vals['meter_id']),
    #             ('reading_date', '<', vals['reading_date'])
    #         ], order='reading_date desc', limit=1)
    #         if last_reading:
    #             vals['previous_reading'] = last_reading.current_reading
    #         else:
    #             meter = self.env['utility.meter'].browse(vals['meter_id'])
    #             vals['previous_reading'] = meter.serial_id.initial_reading if meter.serial_id else 0.0
    #     rec = super().create(vals)
    #     rec._generate_bill()
    #     return rec

    @api.model
    def create(self, vals):
     #print(f"Consumption ")
     if vals.get('meter_id'):
        # Use meter.reset for last reset reading
        last_reset = self.env['meter.reset'].search([
            ('meter_id', '=', vals['meter_id']),
        ], order='reset_date desc', limit=1)
        if last_reset:
            vals['previous_reading'] = last_reset.current_reading
        else:
            # Fallback: use initial reading from serial if available
            meter = self.env['utility.meter'].browse(vals['meter_id'])
            vals['previous_reading'] = meter.serial_id.initial_reading if meter.serial_id else 0.0

    # If this is a reset reading, ignore most fields except meter_id, previous_reading, current_reading
     if vals.get('is_reset_reading'):
        # Only keep the allowed fields for reset
        allowed_fields = {'meter_id', 'previous_reading', 'current_reading', 'is_reset_reading'}
        vals = {k: v for k, v in vals.items() if k in allowed_fields}
        # Optionally, set other fields to default if needed
     #else:
        # Set previous_reading before creation for normal readings
        # if vals.get('meter_id') and vals.get('reading_date'):
        #     last_reading = self.env['meter.reading'].search([
        #         ('meter_id', '=', vals['meter_id']),
        #         ('reading_date', '<', vals['reading_date'])
        #     ], order='reading_date desc', limit=1)
        #     if last_reading:
        #         vals['previous_reading'] = last_reading.current_reading
        #     else:
        #         meter = self.env['utility.meter'].browse(vals['meter_id'])
        #         vals['previous_reading'] = meter.serial_id.initial_reading if meter.serial_id else 0.0
     rec = super().create(vals)
     if not vals.get('is_reset_reading'):
        rec._generate_bill()
     return rec

    # def write(self, vals):
    #     res = super().write(vals)
    #     for rec in self:
    #         if not rec.billed:
    #             rec._generate_bill()
    #     return res


    # filepath: /home/cabdi/odoo/odoo17/custom_addons_2/utility/models/meter_readings.py
    def action_confirm(self):
     for record in self:
            if record.invoice_id.state == 'draft':
                record.invoice_id.action_post()

    def action_cancel(self):
     for record in self:
            if record.invoice_id.state in ['draft']:
                record.invoice_id.button_cancel()

    def action_reset_to_draft(self):
     for record in self:
            if record.invoice_id.state in ['posted']:
                record.invoice_id.button_draft()


    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }