# -*- coding: utf-8 -*-
from openerp import fields, models, api
# from openerp.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ['mail.thread', 'account.payment']

    @api.onchange('journal_id')
    def _onchange_journal(self):
        """
        Sobre escribimos y desactivamos la parte del dominio de la funcion
        original ya que se pierde si se vuelve a entrar
        """
        if self.journal_id:
            self.currency_id = (
                self.journal_id.currency_id or self.company_id.currency_id)
            # Set default payment method
            # (we consider the first to be the default one)
            payment_methods = (
                self.payment_type == 'inbound' and
                self.journal_id.inbound_payment_method_ids or
                self.journal_id.outbound_payment_method_ids)
            self.payment_method_id = (
                payment_methods and payment_methods[0] or False)
        #     # Set payment method domain
        #     # (restrict to methods enabled for the journal and to selected
        #     # payment type)
            payment_type = self.payment_type in (
                'outbound', 'transfer') and 'outbound' or 'inbound'
            return {
                'domain': {
                    'payment_method_id': [
                        ('payment_type', '=', payment_type),
                        ('id', 'in', payment_methods.ids)]}}