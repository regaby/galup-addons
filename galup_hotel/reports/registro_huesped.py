# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
# from osv.orm import browse_record_list
# from osv import osv,fields
import time
# from report_aeroo.currency_to_text import currency_to_text
# from tools.translate import _
from datetime import timedelta, datetime


GENDER={'male': 'Masculino','female': 'Femenino','other': 'Otro'}
MARITAL={'single': 'Soltero'}
class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        