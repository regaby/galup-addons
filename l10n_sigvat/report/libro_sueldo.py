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
            'get_data':self._get_data,
            'get_objects':self._get_objects,

        })


    def _get_data(self,objects):
        cr = self.cr 
        uid = self.uid
        ids = self.localcontext['active_ids']
        ret = self.pool.get('libro.sueldo').read(cr, uid, ids[0])
        ret['mes'] = MONTH[ret['month']]
        partner = self.pool.get('res.partner').browse(cr, uid, ret['employeer_id'][0])
        ret['cuit'] = partner.cuit
        ret['address'] = '%s, %s'%(partner.street,partner.city)
        # print ret
        return ret

    def _get_objects(self,objects):
        cr = self.cr 
        uid = self.uid

        ids = self.localcontext['active_ids']
        ret = self.pool.get('libro.sueldo').read(cr, uid, ids[0])
        print ret['year'][1]
        payroll_ids = self.pool.get('sigvat.payroll').search(cr, uid, [('employeer_id','=',ret['employeer_id'][0]),('month','=',ret['month']),('year','=',ret['year'][0])])
        o = self.pool.get('sigvat.payroll').browse(cr, uid, payroll_ids)
        
        return o

  