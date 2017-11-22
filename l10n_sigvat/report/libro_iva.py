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
            'has_subtotal': self._has_subtotal,
            'get_net': self._get_net,

        })
        self.field_0 = []
        self.acum_field_0 = 0
        self.field_1 = []
        self.acum_field_1 = 0
        self.field_2 = []
        self.acum_field_2 = 0
        self.field_3 = []
        self.acum_field_3 = 0
        self.field_4 = []
        self.acum_field_4 = 0
        self.field_5 = []
        self.acum_field_5 = 0
        self.field_6 = []
        self.acum_field_6 = 0
        self.field_7 = []
        self.acum_field_7 = 0
        self.field_8 = []
        self.acum_field_8 = 0
        self.field_9 = []
        self.acum_field_9 = 0


    def _get_month(self, month):
        return MONTH[month]

    def _get_objects(self):

        cr = self.cr 
        uid = self.uid

        libro_iva = self.localcontext['active_ids']
        o = self.pool.get('sigvat.journal').browse(cr, uid, libro_iva[0])
        return o.purchase_line_ids

    def _get_net(self, lines, tax):
        net=0
        for line in lines:
            if line.vat_tax_id.amount==tax:
                net += line.net_amount
        return net

    def _sumar(self, field):
        summ = 0
        for o in self._get_objects():
            summ+=o[field]

        return summ
    def _push_subtotal(self, value, field):
        if field=='field_0':
            self.field_0.append(value)
            self.acum_field_0 = self.acum_field_0 + value
        if field=='field_1':
            self.field_1.append(value)
            self.acum_field_1 = self.acum_field_1 + value
        if field=='field_2':
            self.field_2.append(value)
            self.acum_field_2 = self.acum_field_2 + value
        if field=='field_3':
            self.field_3.append(value)
            self.acum_field_3 = self.acum_field_3 + value
        if field=='field_4':
            self.field_4.append(value)
            self.acum_field_4 = self.acum_field_4 + value
        if field=='field_5':
            self.field_5.append(value)
            self.acum_field_5 = self.acum_field_5 + value
        if field=='field_6':
            self.field_6.append(value)
            self.acum_field_6 = self.acum_field_6 + value
        if field=='field_7':
            self.field_7.append(value)
            self.acum_field_7 = self.acum_field_7 + value
        if field=='field_8':
            self.field_8.append(value)
            self.acum_field_8 = self.acum_field_8 + value
        if field=='field_9':
            self.field_9.append(value)
            self.acum_field_9 = self.acum_field_9 + value

    def _pop_subtotal(self, field):
        if field=='field_0':
            if len(self.field_0) > 0:
                return self.field_0.pop()
        if field=='field_1':
            if len(self.field_1) > 0:
                return self.field_1.pop()
        if field=='field_2':
            if len(self.field_2) > 0:
                return self.field_2.pop()
        if field=='field_3':
            if len(self.field_3) > 0:
                return self.field_3.pop()
        if field=='field_4':
            if len(self.field_4) > 0:
                return self.field_4.pop()
        if field=='field_5':
            if len(self.field_5) > 0:
                return self.field_5.pop()
        if field=='field_6':
            if len(self.field_6) > 0:
                return self.field_6.pop()
        if field=='field_7':
            if len(self.field_7) > 0:
                return self.field_7.pop()
        if field=='field_8':
            if len(self.field_8) > 0:
                return self.field_8.pop()
        if field=='field_9':
            if len(self.field_9) > 0:
                return self.field_9.pop()



    def _get_subtotal(self, field):
        self._pop_subtotal(field)
        if field=='field_0':
            return self.acum_field_0
        if field=='field_1':
            return self.acum_field_1
        if field=='field_2':
            return self.acum_field_2
        if field=='field_3':
            return self.acum_field_3
        if field=='field_4':
            return self.acum_field_4
        if field=='field_5':
            return self.acum_field_5
        if field=='field_6':
            return self.acum_field_6
        if field=='field_7':
            return self.acum_field_7
        if field=='field_8':
            return self.acum_field_8
        if field=='field_9':
            return self.acum_field_9

    def _has_subtotal(self):
        return len(self.field_9)

