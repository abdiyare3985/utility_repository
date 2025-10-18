from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError


class SahalImport(models.Model):
    _name = 'sahal.import'
    _description = 'Sahal Import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    transfer_id = fields.Char(string='Transfer ID')
    transaction_id = fields.Char(string='Transaction ID')
    transfer_date = fields.Datetime(string='Transfer Date')
    description = fields.Char(string='Description')
    other_party_account = fields.Char(string='Other Party Account')
    debit = fields.Char(string='Debit')
    credit = fields.Char(string='Credit')
    balance = fields.Float(string='Balance')
    status = fields.Selection(
        [
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='pending',
        required=True,
        tracking=True,
    )
    sender_mobile = fields.Char(string='Sender Mobile', compute='_compute_sender_mobile', store=True)
    customer_id = fields.Many2one('res.partner', string='Customer',  ondelete='cascade', domain=[('customer_rank', '>', 0)], unique=True)

    payment_ids = fields.One2many(
        'account.payment', 
        'transfer_id', 
        string='Payments',
        compute='_compute_payment_ids',
        store=False,
    )
    payment_line_ids = fields.One2many('sahal.import.payment.line', 'sahal_import_id', string='Payment Lines')
    split_payment = fields.Boolean(string="Split Payment")

    previous_mobile_payment_count = fields.Integer(
    string="Previous Mobile Payments",
    compute='_compute_previous_mobile_payment_count'
)
    account = fields.Char(string='Account')

    def _compute_previous_mobile_payment_count(self):
     for record in self:
        domain = [
            ('mobile_sender', '=', record.sender_mobile),
            ('transfer_id', '!=', record.transfer_id),
        ]
        record.previous_mobile_payment_count = self.env['account.payment'].search_count(domain)

    @api.depends('description')
    def _compute_sender_mobile(self):
        for record in self:
            mobile = False
            if record.description:
                # Try to extract after 'from :'
                match_from = re.search(r'from\s*:\s*(\d+)', record.description, re.IGNORECASE)
                if match_from:
                    mobile = match_from.group(1)
                else:
                    # Fallback to 252 pattern
                    match_252 = re.search(r'(252\d{7,})', record.description)
                    if match_252:
                        mobile = match_252.group(1)
            record.sender_mobile = mobile

    @api.depends('transfer_id')
    def _compute_payment_ids(self):
        for record in self:
            if record.transfer_id:
                record.payment_ids = self.env['account.payment'].search([('transfer_id', '=', record.transfer_id)])
            else:
                record.payment_ids = self.env['account.payment']

    # def action_complete(self):
    #     # Prepare values for account.payment
    #     payment_vals = {
    #         'partner_id': self.customer_id.id,
    #         'amount': float(self.credit or 0),
    #         'date': self.transfer_date or fields.Date.context_today(self),
    #         'trans_ref': self.description,
    #         'mobile_sender': self.sender_mobile,
    #         'transfer_id': self.transfer_id,
    #         'payment_type': 'inbound' ,
    #         'partner_type': 'customer',
    #         'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
    #     }
    #     payment = self.env['account.payment'].create(payment_vals)
    #     # Optionally, post the payment
    #     payment.action_post()
    #     self.status = 'completed'

    # def action_complete(self):
    #  if self.payment_line_ids:
    #     # Split payment: create a payment for each line
    #     for line in self.payment_line_ids:
    #         payment_vals = {
    #             'partner_id': line.partner_id.id,
    #             'amount': line.amount,
    #             'date': self.transfer_date or fields.Date.context_today(self),
    #             'trans_ref': self.description,
    #             'mobile_sender': self.sender_mobile,
    #             'transfer_id': self.transfer_id,
    #             'payment_type': 'inbound',
    #             'partner_type': 'customer',
    #             'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
    #         }
    #         payment = self.env['account.payment'].create(payment_vals)
    #         payment.action_post()
    #  else:
    #     # Single payment: pay the whole credit to the main customer
    #     payment_vals = {
    #         'partner_id': self.customer_id.id,
    #         'amount': float(self.credit or 0),
    #         'date': self.transfer_date or fields.Date.context_today(self),
    #         'trans_ref': self.description,
    #         'mobile_sender': self.sender_mobile,
    #         'transfer_id': self.transfer_id,
    #         'payment_type': 'inbound',
    #         'partner_type': 'customer',
    #         'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
    #     }
    #     payment = self.env['account.payment'].create(payment_vals)
    #     payment.action_post()
    #  self.status = 'completed'


#     def action_complete(self):
#      for record in self:
#         # Validation
#         if record.split_payment:
#             if not record.payment_line_ids:
#                 raise ValidationError("At least one payment line is required when Split Payment is enabled.")
#             for line in record.payment_line_ids:
#                 if not line.partner_id or not line.amount:
#                     raise ValidationError("Each payment line must have a partner and an amount.")
#             # Split payment: create a payment for each line
#             for line in record.payment_line_ids:
#                 payment_vals = {
#                     'partner_id': line.partner_id.id,
#                     'amount': line.amount,
#                     'date': record.transfer_date or fields.Date.context_today(record),
#                     'trans_ref': record.description,
#                     'mobile_sender': record.sender_mobile,
#                     'transfer_id': record.transfer_id,
#                     'payment_type': 'inbound',
#                     'partner_type': 'customer',
#                     'journal_id': record.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
#                 }
#                 payment = record.env['account.payment'].create(payment_vals)
#                 payment.action_post()
#         else:
#             if not record.customer_id:
#                 raise ValidationError("Customer is required when Split Payment is not enabled.")
#             # Single payment: pay the whole credit to the main customer
#             # payment_vals = {
#             #     'partner_id': record.customer_id.id,
#             #     'amount': float(record.credit or 0),
#             #     'date': record.transfer_date or fields.Date.context_today(record),
#             #     'trans_ref': record.description,
#             #     'mobile_sender': record.sender_mobile,
#             #     'transfer_id': record.transfer_id,
#             #     'payment_type': 'inbound',
#             #     'partner_type': 'customer',
#             #     'journal_id': record.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
#             # }
#             # payment = record.env['account.payment'].create(payment_vals)
#             payments = self.env['account.payment'].search([
#     ('partner_id', '=', 41193),
#     ('transfer_id', '=', record.transfer_id)
# ])
#             for payment in payments:
#                 payment.partner_id = record.customer_id.id
#            # payment.action_post()
#         record.status = 'completed'


    def action_complete(self):
     for record in self:
        journal = False
        if record.account:
            journal = record.env['account.journal'].search([('name', 'ilike', record.account)], limit=1)
        if not journal:
            journal = record.env['account.journal'].search([('type', '=', 'bank')], limit=1)

        if record.split_payment:
            # Find and cancel/delete payment(s) for partner 41193 and this transfer
            payments_41193 = self.env['account.payment'].search([
                ('partner_id', '=', 41193),
                ('transfer_id', '=', record.transfer_id)
            ])
            for payment in payments_41193:
                payment.action_draft()
                payment.unlink()
                #payment.cancel()  # or payment.unlink() to delete

            # Create payments for each line
            if not record.payment_line_ids:
                raise ValidationError("At least one payment line is required when Split Payment is enabled.")
            for line in record.payment_line_ids:
                if not line.partner_id or not line.amount:
                    raise ValidationError("Each payment line must have a partner and an amount.")
                payment_vals = {
                    'partner_id': line.partner_id.id,
                    'amount': line.amount,
                    'date': record.transfer_date or fields.Date.context_today(record),
                    'trans_ref': record.description,
                    'mobile_sender': record.sender_mobile,
                    'transfer_id': record.transfer_id,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'journal_id': journal.id,
                }
                payment = record.env['account.payment'].create(payment_vals)
                payment.action_post()
        else:
            if not record.customer_id:
                raise ValidationError("Customer is required when Split Payment is not enabled.")
            # Update payment from 41193 to customer_id
            payments = self.env['account.payment'].search([
                ('partner_id', '=', 41193),
                ('transfer_id', '=', record.transfer_id)
            ])
            for payment in payments:
                payment.partner_id = record.customer_id.id
        record.status = 'completed'

    def action_cancel(self):
        self.status = 'cancelled'

    def action_reset_to_pending(self):
        self.status = 'pending'

    def action_view_payments(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_payments').read()[0]
        action['domain'] = [('transfer_id', '=', self.transfer_id)]
        action['context'] = dict(self.env.context)
        return action
    
    # def action_view_previous_mobile_payments(self):
    #  self.ensure_one()
    #  action = self.env.ref('account.action_account_payments').read()[0]
    #  action['domain'] = [('mobile_sender', '=', self.sender_mobile)]
    #  action['context'] = dict(self.env.context)
    #  return action

    def action_view_previous_mobile_payments(self):
     self.ensure_one()
     action = self.env.ref('account.action_account_payments').read()[0]
     action['domain'] = [
        ('mobile_sender', '=', self.sender_mobile),
        ('transfer_id', '!=', self.transfer_id),
    ]
     action['context'] = dict(self.env.context)
     return action
    
    @staticmethod
    def _safe_float(value):
        try:
           return float(value)
        except (ValueError, TypeError):
           return 0.0

    @api.model
    def create(self, vals):
     if 'status' not in vals:
        vals['status'] = 'pending'

     record = super(SahalImport, self).create(vals)

    # Find the journal by account code in its name
     journal = False
     if record.account:
        journal = record.env['account.journal'].search([('name', 'ilike', record.account)], limit=1)
     if not journal:
        journal = record.env['account.journal'].search([('type', '=', 'bank')], limit=1)

    # Always use partner_id 41193
    # partner_id = 41193
     partner_id = 30710

     amount = self._safe_float(record.credit)
     if amount > 0:
        payment_vals = {
            'partner_id': partner_id,
            'amount': amount,
            'date': record.transfer_date or fields.Date.context_today(record),
            'trans_ref': record.description,
            'mobile_sender': record.sender_mobile,
            'transfer_id': record.transfer_id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'journal_id': journal.id,
        }
        payment = record.env['account.payment'].create(payment_vals)
        payment.action_post()
    # else: do not create payment if amount is zero or negative

     return record
