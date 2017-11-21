# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
# from osv.orm import browse_record_list
# from osv import osv,fields
import time
# from report_aeroo.currency_to_text import currency_to_text
# from tools.translate import _
from datetime import timedelta, datetime

MONTH={'01': 'Enero','02': 'Febrero','03': 'Marzo','04': 'Abril','05': 'Mayo','06': 'Junio','07': 'Junio','08': 'Agosto','09': 'Septiembre','10': 'Octubre','11': 'Noviembre','12': 'Diciembre'}

class Parser(report_sxw.rml_parse):

    

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_month':self._get_month,
            'get_objects':self._get_objects,
            'sumar': self._sumar,
            'push_subtotal': self._push_subtotal,
            'get_subtotal': self._get_subtotal,
            'pop_subtotal': self._pop_subtotal,

        })
        self.subtotales=[]
        self.acumulado = 0

    

    def _get_month(self, month):
        return MONTH[month]

    def _get_objects(self, objects):

        cr = self.cr 
        uid = self.uid

        libro_iva = self.localcontext['active_ids']
        o = self.pool.get('sigvat.journal').browse(cr, uid, libro_iva[0])
        return o.purchase_line_ids

    def _sumar(self, field):
        summ = 0
        for o in self._get_objetos():
            summ+=o[field]

        return summ
    def _push_subtotal(self, value):
        self.subtotales.append(value)
        self.acumulado = self.acumulado + value

    def _pop_subtotal(self):
        if len(self.subtotales) > 0:
            return self.subtotales.pop()

    def _get_subtotal(self):
        # return self.subtotales
        self._pop_subtotal()
        return self.acumulado

