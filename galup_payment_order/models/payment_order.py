# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from openerp import models, fields, api, exceptions, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp import tools
import requests
from openerp.exceptions import UserError


class PaymentOrder(models.Model):
    _name = "payment.order"

    name = fields.Char(string='Payment Order Number', required=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('payment.order'))
    date = fields.Date(string='Payment Order Date', required=True)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    invoice_ids = fields.Many2many('account.invoice', 'payment_order_invoice_rel', 'payment_order_id',
                                   'invoice_id', string='Invoices', copy=False)
