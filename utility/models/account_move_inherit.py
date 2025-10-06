from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    meter_reading_id = fields.Many2one('meter.reading', string='Meter Reading', readonly=True)
    partner_meter_id = fields.Many2one(
        'utility.meter',
        string='Meter',
        related='partner_id.meter_id',
        store=False,
        readonly=True,
    )

    partner_display_name = fields.Char(
        string='Customer Name',
        related='partner_id.display_name',
        store=False,
        readonly=True,
    )
    

    # previous_balance = fields.Monetary(
    #     string='Previous Balance',
    #     compute='_compute_previous_balance',
    #     currency_field='currency_id'
    # )

    # @api.depends('partner_id', 'invoice_date')
    # def _compute_previous_balance(self):
    #     for move in self:
    #         if move.partner_id and move.invoice_date:
    #             domain = [
    #                 ('partner_id', '=', move.partner_id.id),
    #                 ('move_type', 'in', ['out_invoice', 'out_refund']),
    #                 ('state', '=', 'posted'),
    #                 ('invoice_date', '<', move.invoice_date),
    #             ]
    #             moves = self.env['account.move'].search(domain)
    #             move.previous_balance = sum(m.amount_total_signed for m in moves)
    #         else:
    #             move.previous_balance = 0.0

    # def get_previous_balance(self):
    #     self.ensure_one()
    #     # Get all posted entries for this partner before this invoice date
    #     domain = [
    #         ('partner_id', '=', self.partner_id.id),
    #         ('move_type', 'in', ['out_invoice', 'out_refund']),
    #         ('state', '=', 'posted'),
    #         ('invoice_date', '<', self.invoice_date),
    #     ]
    #     moves = self.env['account.move'].search(domain)
    #     # Sum all amounts (invoices positive, refunds negative)
    #     balance = sum(m.amount_total_signed for m in moves)
    #     return balance



    def action_post(self):
        print(f"Credits before posting: {[ (inv.partner_id.name, inv.partner_id.credit) for inv in self ]}")
        res = super(AccountMove, self).action_post()
        for move in self:
            print(f"Processing move {move.partner_id.credit} with state {move.state}")
            if move.state == 'posted' and move.partner_id.credit < 0:
               print(f'posted...............................{move.partner_id.credit}')
               #print(f"Invoice {move.name or move.id} is now posted for customer {move.partner_id.name}")
            # You can access all fields of the posted invoice here
           # if successfully_posted:
               self.reconcile_invoice_credits(move)
        return res
    


    def reconcile_invoice_credits(self, invoice):
    
     invoice_receivable_lines = invoice.line_ids.filtered(
        lambda l: l.account_id.account_type == 'asset_receivable' and not l.reconciled
    )
    
     if not invoice_receivable_lines:
        return False
    
     ar_account_id = invoice_receivable_lines[0].account_id.id
    
    # Find available credit lines for this partner
     credit_lines = self.env['account.move.line'].search([
        ('partner_id', '=', invoice.partner_id.id),
        ('account_id', '=', ar_account_id),
        ('move_id.state', '=', 'posted'),
        ('reconciled', '=', False),
        ('balance', '<', 0),
    ], order='date asc')  # Using order parameter instead of sorted()
    
    # Reconcile line by line
     for c_line in credit_lines:
        if not invoice_receivable_lines:
            break
        (c_line + invoice_receivable_lines).reconcile()
        invoice_receivable_lines = invoice_receivable_lines.filtered(lambda l: not l.reconciled)
    
     return True