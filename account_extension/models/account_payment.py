# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class account_payment(models.Model):
    _name = "account.payment"
    _inherit = 'account.payment'

    name = fields.Char(readonly=True, copy=False, default="Pago Borrador")

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError(_('The payment amount must be strictly positive.'))