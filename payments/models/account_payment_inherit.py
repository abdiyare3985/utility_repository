from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    zone_id =fields.Many2one('utility.meter.zone', string='Zone')
    balance = fields.Float(string="Balance")
    mobile_sender = fields.Char(string="Mobile Sender")
    trans_ref = fields.Char(string="Transaction Reference")
    transfer_id = fields.Char(string="Transaction ID")


    @api.onchange('partner_id')
    def _onchange_partner_id_set_balance(self):
        if self.partner_id:
            # Search for posted customer invoices (and refunds) that are not fully paid
            invoices = self.env['account.move'].search([
                ('partner_id', '=', self.partner_id.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
            ])
            print(f"Found {len(invoices)} invoices for partner {self.partner_id.meter_id} ({self.partner_id.id})")
            print(f"Partner name: {self.partner_id.name}")
            zone_id= self.env['utility.meter.zone'].search([('name', '=', self.partner_id.meter_id.zone_id.name)], limit=1)
            self.zone_id = zone_id if zone_id else False
            #print(f"Found zone: {self.zone_id.id if self.zone_id else 'None'} for partner {self.partner_id.billing_account} ({self.partner_id.id})")
            # Sum the residual amount from each invoice as the due balance
            self.balance = sum(invoice.amount_residual for invoice in invoices)
        else:
            self.balance = 0.0

    @api.model
    def create(self, vals):
        # Create a new payment record
        record = super(AccountPayment, self).create(vals)
        # After creation, if a partner is set, compute the balance and zone_id
        if record.partner_id:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', record.partner_id.id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
            ])
            record.balance = sum(inv.amount_residual for inv in invoices) or 0.0
            zone_id= self.env['utility.meter.zone'].search([('name', '=', self.partner_id.meter_id.zone_id.name)], limit=1)
            #print(f"Creating payment for partner {record.partner_id.billing_account} ({record.partner_id.id}), found zone: {zone_id.id if zone_id else 'None'}")
            record.zone_id = zone_id if zone_id else False
            
        return record
    

   

    
    

    def action_post(self):
   
     try:
        for payment in self:
            # Validate payment first
            if not payment.partner_id:
                raise UserError(_("You must select a Customer before posting the payment."))
            if payment.amount <= 0:
                raise UserError(_("Payment amount must be greater than zero."))

            # Create a savepoint
            with self.env.cr.savepoint():
                # 1. Post the payment
                super(AccountPayment, payment).action_post()
                
                # 2. Find matching invoices
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', payment.partner_id.id),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('move_type', 'in', ['out_invoice', 'in_invoice'])
                ], order='invoice_date asc')

                remaining_payment = payment.amount
                
                # 3. Reconcile with invoices
                for invoice in invoices:
                    if remaining_payment <= 0:
                        break

                    if invoice.state != 'posted':
                       invoice.action_post()

                    amount_to_apply = min(remaining_payment, invoice.amount_residual)
                    if amount_to_apply > 0:
                        receivable_lines = invoice.line_ids.filtered(
                            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled
                        )
                        payment_lines = payment.move_id.line_ids.filtered(
                            lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled
                        )
                        
                        if receivable_lines and payment_lines:
                            (receivable_lines + payment_lines).reconcile()
                            remaining_payment -= amount_to_apply


                
                
                # 5. Handle overpayment
                if remaining_payment > 0:
                    _logger.warning(f"Overpayment detected for payment {payment.id}: {remaining_payment}")
                    
        return True

     except Exception as e:
        _logger.error("Payment posting failed: %s", str(e), exc_info=True)
        raise UserError(_("Payment posting failed: %s") % str(e))


    # Example: Use Register Payment wizard to pay and reconcile open invoices for a partner
    # def action_print_receipt(self):
    #  return {
    #     'type': 'ir.actions.report',
    #     'report_name': 'payments.payment_reciept_report_pdf',
    #     'report_type': 'qweb-pdf',
    #     'res_id': self.id,
    #     'target': 'new',  # This opens in a new tab
    # }

    def action_print_receipt(self):
        print("Printing receipt...")
        data = {
            
            'payment_id': self.id,
        }
        return self.env.ref('payments.payment_reciept_report_pdf').report_action([], data=data)

    


    

    




   