# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id',
                 'company_id', 'date_invoice', 'type')
    def _compute_amount_percep(self):
        ## este metodo resta al amount_total todo lo que no sea iva
        amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        amount_tax = sum(line.amount for line in self.tax_line_ids)
        amount_total = amount_untaxed + amount_tax
        percep = 0
        for tax_line in self.tax_line_ids:
            if tax_line.tax_id.description != 'IVA 21%':
                percep += tax_line.amount
        self.amount_untaxed_percep = amount_total - percep


    amount_untaxed_percep = fields.Monetary(string='Untaxed Amount Percep', store=True,
                                            readonly=True, compute='_compute_amount_percep',
                                            track_visibility='always')

