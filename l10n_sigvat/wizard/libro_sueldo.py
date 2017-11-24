# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
# from odoo.tools.float_utils import float_round
# from odoo.exceptions import UserError
import base64
import time
from datetime import datetime, timedelta


class libro_sueldo(models.TransientModel):
    """
    Wizard para generar archivo AFIP regimen información Compra Venta
    """
    _name = "libro.sueldo"
    _description = "Libro Sueldo Ministerio de Trabajo"

    month = fields.Selection(default='01', string="Mes", required=True,
        selection=[
            ('01', 'Enero'),
            ('02', 'Febrero'),
            ('03', 'Marzo'),
            ('04', 'Abril'),
            ('05', 'Mayo'),
            ('06', 'Junio'),
            ('07', 'Julio'),
            ('08', 'Agosto'),
            ('09', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),])
    year = fields.Many2one("account.fiscal.position", string='Ejercicio', ondelete='restrict', required=True)
    employeer_id = fields.Many2one('res.partner', 'Empleador', domain="[('is_employeer','=','True')]", required=True)
    format = fields.Selection( string='Formato Reporte',selection=[('horizontal','Horizontal'),('vertical','Vertical')], default='vertical', required=True)

    @api.multi
    def print_report(self):
        wizard = self.read()[0]
        print wizard
        datas = {
             'form': wizard
        }
        report_name = 'libro_sueldo_%s'%wizard['format']

        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'data': datas,
        }

libro_sueldo()
