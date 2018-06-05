# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
# from osv.orm import browse_record_list
# from osv import osv,fields
import time
# from report_aeroo.currency_to_text import currency_to_text
# from tools.translate import _
from datetime import timedelta, datetime
from openerp.addons.amount_to_text_es import amount_to_text_es
from openerp.tools.float_utils import float_round
import math


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'amount_to_text':self._amount_to_text,
            'get_objects':self._get_objects,
            
        })
        
    def _amount_to_text(self, amount_total):
        amount_in_words = amount_to_text_es.amount_to_text(math.floor(amount_total), lang='es', currency='')
        amount_in_words = amount_in_words.replace(' and Zero Cent', '') # Ugh
        decimals = amount_total % 1
        if decimals >= 10**-2:
            amount_in_words += _(' and %s/100') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return amount_in_words

    def _get_objects(self, objects, context=None):
        active_id = self.localcontext['active_ids'][0]
        cr = self.cr
        uid = self.uid
        obj = self.pool.get('hotel.payment').browse(cr, uid, active_id)
        if obj.folio_id:
            vals = {
                'website': obj.folio_id.warehouse_id.partner_id.website,
                'city': obj.folio_id.warehouse_id.partner_id.city,
                'state_id': obj.folio_id.warehouse_id.partner_id.state_id,
                'country_id': obj.folio_id.warehouse_id.partner_id.country_id,
                'partner_id': obj.folio_id.partner_id.name,
                'partner_street': obj.folio_id.partner_id.street,
                'partner_city': obj.folio_id.partner_id.city,
                'partner_state_id': obj.folio_id.partner_id.state_id,
                'partner_country_id': obj.folio_id.partner_id.country_id,
                'partner_phone': obj.folio_id.partner_id.phone,
                'amount_total': obj.amount,
                'fecha_pago': obj.payment_date,
                'concepto': 'Pago de alojamiento.-',
                'metodo_de_pago': obj.journal_id,
            }
        else:
            vals = {
                'website': obj.reservation_id.warehouse_id.partner_id.website,
                'city': obj.reservation_id.warehouse_id.partner_id.city,
                'state_id': obj.reservation_id.warehouse_id.partner_id.state_id,
                'country_id': obj.reservation_id.warehouse_id.partner_id.country_id,
                'partner_id': obj.reservation_id.partner_id.name,
                'partner_street': obj.reservation_id.partner_id.street,
                'partner_city': obj.reservation_id.partner_id.city,
                'partner_state_id': obj.reservation_id.partner_id.state_id,
                'partner_country_id': obj.reservation_id.partner_id.country_id,
                'partner_phone': obj.reservation_id.partner_id.phone,
                'amount_total': obj.amount,
                'fecha_pago': obj.payment_date,
                'concepto': 'Seña de alojamiento.-',
                'metodo_de_pago': obj.journal_id,
            }
        ret = []
        ret.append(vals)
        return ret
        