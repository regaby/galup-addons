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
            
        })
        
    def _amount_to_text(self, amount_total):
        amount_in_words = amount_to_text_es.amount_to_text(math.floor(amount_total), lang='es', currency='')
        amount_in_words = amount_in_words.replace(' and Zero Cent', '') # Ugh
        decimals = amount_total % 1
        if decimals >= 10**-2:
            amount_in_words += _(' and %s/100') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return amount_in_words

    