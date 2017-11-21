# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
# from odoo.tools.float_utils import float_round
# from odoo.exceptions import UserError
import base64
import time
from datetime import datetime, timedelta


class sigvat_reginfo_cv(models.TransientModel):
    """
    Wizard para generar archivo AFIP regimen información Compra Venta
    """
    _name = "sigvat.reginfo.cv"
    _description = "AFIP regimen informacion Compra Venta"
    # _columns = {
    #             'data': fields.binary('File', readonly=True),
    #             'name': fields.char('Filename', 16, readonly=True),
    #             'state': fields.selection( ( ('choose','choose'),
    #                  ('get','get'),
    #                ) ),
    #             }
    data = fields.Binary(string='File', readonly=True)
    name = fields.Char(string='Filename', size=16, readonly=True)
    state = fields.Selection( string='State',selection=[('choose','choose'),('get','get'),('error','error')], default='choose')
    info = fields.Text('Info', readonly=True)

    @api.multi
    def generate_header(self):
        this = self
        o = self.env['sigvat.journal'].browse(self._context.get('active_id', []))
        output = ''
        outerr = ''

        if not o.partner_id.cuit:
            outerr += _('El proveedor %s no posee CUIT '%(o.partner_id.name))
        else:
            output += str(o.partner_id.cuit).replace('-','').zfill(11) # 1- CUIL/CUIT
            output += str(o.year.name)+str(o.month) # 2- Periodo AAAAMM
            output += str(o.sequence) # 3- Secuencia, por defecto 00
            output += str(o.no_movements) # 4- Sin movimientos, por defecto N
            output += str(o.pro_cred_fiscal_comp) # 5- prorratear credito fiscal computable, por defecto N
            output += ' ' # 6- credito fiscal computable global o por comprobante
            output += '0'.zfill(15) # 7- importe credito fiscal computable global
            output += '0'.zfill(15) # 8- importe credito fiscal computable global, con asignacion directa
            output += '0'.zfill(15) # 9- importe credito fiscal computable global, determinado por prorrateo
            output += '0'.zfill(15) # 10- importe credito fiscal no computable global
            output += '0'.zfill(15) # 11- credito fiscal contrib. seg. soc. y otros conceptos
            output += '0'.zfill(15) # 12- credito fiscal computable seg. soc. y otros conceptos
            output+= '\r\n'
        

        if outerr=="":
            filename = 'cabecera.txt'
            out=base64.encodestring(output.encode('utf-8'))
            self.state = 'get'
            self.data = out
            self.name = filename
        else:
            out=base64.encodestring(outerr.encode('utf-8'))
            self.state = 'error'
            self.info = outerr
            self.name = ''
        view_id = self.env['ir.ui.view'].search([('model','=','sigvat.reginfo.cv')], limit=1).id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sigvat.reginfo.cv',
            'name': _('Generar Formulario 931'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
             'nodestroy': True,
             'context': self._context
                }

    @api.multi
    def generate_purchase(self):
        this = self
        o = self.env['sigvat.journal'].browse(self._context.get('active_id', []))
        output = ''
        outerr = ''

        if not o.purchase_line_ids:
            outerr += 'El registro no tiene lineas de compra'

        for l in o.purchase_line_ids:
            output += str(datetime.strptime(l.date, '%Y-%m-%d').strftime('%Y%m%d')) # 1- fecha comprobante AAAAMMDD
            output += str(l.voucher_type_id.cod) # 2- Tipo de comprobante
            output += str(l.point_of_sale).zfill(5) # 3- punto de venta
            output += str(l.voucher_number).zfill(20) # 4- Numero de comprobante
            output += ' '.rjust(16) # 5- Despacho de importación
            output += str(l.partner_id.document_type) # 6- cod. de documento del vendedor
            if not l.partner_id.cuit:
                outerr += _('El proveedor %s no posee CUIT '%(l.partner_id.name))
                break
            output += str(l.partner_id.cuit).replace('-','').zfill(20) # 7- numero de identificación del vendedor
            output += str(l.partner_id.name).rjust(30) # 8 - Apellido y nombre vendedor
            output += str(('%.2f')%l.total_amount).replace('.','').zfill(15) # 9 - importe total
            print l.total_amount
            print l.total_amount
            print l.total_amount
            output += '0'.zfill(15)# 10- op. no gravado
            output += '0'.zfill(15)# 11- op. exentas
            output += str(('%.2f')%l.vat_percep_amount).replace('.','').zfill(15)# 12- percepcion IVA
            output += '0'.zfill(15)# 13- percep. otros impuestos nacionales
            output += str(('%.2f')%l.gross_amount).replace('.','').zfill(15) # 14- percep. ingresos brutos
            output += str(('%.2f')%l.municipal_amount).replace('.','').zfill(15) # 15- percep. impuestos municipales
            output += str(('%.2f')%l.internal_amount).replace('.','').zfill(15) # 16- impuesto interno
            output += str(l.currency_id.code)# 17- codigo de moneda
            # output += str(l.currency_id.rate).replace('.','').zfill(10) # 18- tipo de cambio
            output += '1000000'.zfill(10)# 18- tipo de cambio
            output += '1' # 19- cant. alicuotas de iva TODO: preguntar a pablo
            output += str(l.operation_code) # 20- codigo de operacion
            output += str(('%.2f')%l.vat_amount).replace('.','').zfill(15) # 21- credito fiscal computable
            output += '0'.zfill(15) # 22- otros tributos
            output += '0'.zfill(11) # 23- cuit emisor/corredor
            output += ' '.rjust(30) # 24- denominacion emisor/corredor
            output += '0'.zfill(15) # 25- iva comision

            output+= '\r\n'
        

        if outerr=="":
            filename = 'compra.txt'
            out=base64.encodestring(output.encode('utf-8'))
            self.state = 'get'
            self.data = out
            self.name = filename
        else:
            out=base64.encodestring(outerr.encode('utf-8'))
            self.state = 'error'
            self.info = outerr
            self.name = ''
        view_id = self.env['ir.ui.view'].search([('model','=','sigvat.reginfo.cv')], limit=1).id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sigvat.reginfo.cv',
            'name': _('Generar Formulario 931'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
             'nodestroy': True,
             'context': self._context
                }

    @api.multi
    def generate_sale(self):
        this = self
        o = self.env['sigvat.journal'].browse(self._context.get('active_id', []))
        output = ''
        outerr = ''

        if not o.sale_line_ids:
            outerr += 'El registro no tiene lineas de Venta'

        for l in o.sale_line_ids:
            if o.partner_id.cuit == l.partner_id.cuit:
                outerr += _('El numero de identificacion del comprador %s no puede ser la CUIT del informante. '%(l.partner_id.name))
            output += str(datetime.strptime(l.date, '%Y-%m-%d').strftime('%Y%m%d')) # 1- fecha comprobante AAAAMMDD
            output += str(l.voucher_type_id.cod) # 2- Tipo de comprobante
            output += str(l.point_of_sale).zfill(5) # 3- punto de venta
            output += str(l.voucher_number).zfill(20) # 4- Numero de comprobante
            output += str(l.voucher_number).zfill(20) # 5- Numero de comprobante hasta
            output += str(l.partner_id.document_type) # 6- cod. de documento del vendedor
            if l.partner_id.document_type=='80':
                if not l.partner_id.cuit:
                    outerr += _('El proveedor %s no posee CUIT '%(l.partner_id.name))
                    break
                output += str(l.partner_id.cuit).replace('-','').zfill(20) # 7- numero de identificación del vendedor
            else:
                if l.partner_id.reference:
                    output += str(l.partner_id.reference).replace('-','').zfill(20) # 7- numero de identificación del vendedor
                else:
                    outerr += 'The field identification number for the partner %s must be assigned. '%(l.partner_id.name)
                    break
            output += str(l.partner_id.name).rjust(30) # 8 - Apellido y nombre vendedor
            output += str(('%.2f')%l.total_amount).replace('.','').zfill(15) # 9 - importe total
            output += '0'.zfill(15)# 10- op. no gravado
            output += '0'.zfill(15)# 11- percepcion a no categorizados
            output += '0'.zfill(15)# 12- op. exentas
            output += str(('%.2f')%l.vat_amount).replace('.','').zfill(15) # 13- percep. otros impuestos nacionales
            output += str(('%.2f')%l.gross_amount).replace('.','').zfill(15) # 14- percep. ingresos brutos
            output += str(('%.2f')%l.municipal_amount).replace('.','').zfill(15) # 15- percep. impuestos municipales
            output += str(('%.2f')%l.internal_amount).replace('.','').zfill(15) # 16- impuesto interno
            output += str(l.currency_id.code)# 17- codigo de moneda
            # output += str(l.currency_id.rate).replace('.','').zfill(10) # 18- tipo de cambio
            output += '1000000'.zfill(10)# 18- tipo de cambio
            output += '1' # 19- cant. alicuotas de iva TODO: preguntar a pablo
            output += str(l.operation_code) # 20- codigo de operacion
            output += '0'.zfill(15) # 21- otros tributos
            output += str(datetime.strptime(l.date, '%Y-%m-%d').strftime('%Y%m%d')) # 22- fecha vencimiento de pago AAAAMMDD

            output+= '\r\n'
        

        if outerr=="":
            filename = 'venta.txt'
            out=base64.encodestring(output.encode('utf-8'))
            self.state = 'get'
            self.data = out
            self.name = filename
        else:
            out=base64.encodestring(outerr.encode('utf-8'))
            self.state = 'error'
            self.info = outerr
            self.name = ''
        view_id = self.env['ir.ui.view'].search([('model','=','sigvat.reginfo.cv')], limit=1).id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sigvat.reginfo.cv',
            'name': _('Generar Formulario 931'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
             'nodestroy': True,
             'context': self._context
                }

sigvat_reginfo_cv()
