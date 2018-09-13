# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
# from zklib import zklib
import requests
from openerp.exceptions import UserError
from lxml import etree


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    check_ids = fields.Many2many(
        'account.check',
        string='Checks',
        copy=False,
    )

    def get_payment_vals(self):
        """ Hook for extension """
        res = super(account_register_payments, self).get_payment_vals()
        res['check_ids'] = self.check_ids and [(6, 0, self.check_ids.ids)] or False
        print 'res', res
        return res