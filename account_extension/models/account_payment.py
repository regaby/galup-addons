# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class account_payment(models.Model):
    _name = "account.payment"
    _inherit = 'account.payment'

    name = fields.Char(readonly=True, copy=False, default="Pago Borrador")