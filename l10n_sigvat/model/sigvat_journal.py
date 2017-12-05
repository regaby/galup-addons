# -*- encoding: utf-8 -*-
##############################################################################
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp import models, fields, api, _, exceptions
from datetime import datetime
from datetime import timedelta
import time
import calendar
from openerp.exceptions import UserError, AccessError



class SigVatJournal(models.Model):

    _name= 'sigvat.journal'

    @api.one
    @api.depends('purchase_line_ids')
    def _compute_amount(self):
        for line in self.purchase_line_ids:
            if line.vat_tax_id.amount==10.5:
                self.net_10_amount += line.net_amount
            if line.vat_tax_id.amount==21:
                self.net_21_amount += line.net_amount
            if line.vat_tax_id.amount==27:
                self.net_27_amount += line.net_amount
            self.total_amount += line.total_amount
            self.vat_amount += line.vat_amount
            self.municipal_amount += line.municipal_amount
            self.internal_amount += line.internal_amount
            self.vat_percep_amount += line.vat_percep_amount
            self.gross_amount += line.gross_amount
        

    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    month = fields.Selection(string="Month", required=True,
        selection=[
            ('01', 'January'),
            ('02', 'February'),
            ('03', 'March'),
            ('04', 'April'),
            ('05', 'May'),
            ('06', 'June'),
            ('07', 'July'),
            ('08', 'Augost'),
            ('09', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'Dicember'),])
    year = fields.Many2one("account.fiscal.position", string='Year', ondelete='restrict', required=True)
    journal_type = fields.Selection(selection=[('sale','sale'),('purchase','purchase')])  
    sequence = fields.Char(size=2, default='00', required=True, readonly=True)
    no_movements = fields.Selection(selection=[('S','SI'),('N','NO')], default='N', required=True, readonly=True)
    pro_cred_fiscal_comp = fields.Selection( string="Prorratear Crédito Fiscal Computable" ,selection=[('S','SI'),('N','NO')], default='N', required=True, readonly=True)
    purchase_line_ids = fields.One2many ('sigvat.purchase.line', 'journal_id','Vat Purchase Line')
    sale_line_ids = fields.One2many ('sigvat.sale.line', 'journal_id','Vat Sale Line')

    net_10_amount = fields.Float(string='Neto 10.5%', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    net_21_amount = fields.Float(string='Neto 21%', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    net_27_amount = fields.Float(string='Neto 27%', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    total_amount = fields.Float(string='Total Facturado', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    vat_amount = fields.Float(string='Iva Factura', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    municipal_amount = fields.Float(string='Percepcion Municipal', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    internal_amount = fields.Float(string='Impuesto Interno', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    vat_percep_amount = fields.Float(string='Percepcion Iva', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')
    gross_amount = fields.Float(string='Monto Bruto', digits=(13, 2),
        store=False, readonly=False, compute='_compute_amount')



class SigVatPurchaseLine(models.Model):

    _name= 'sigvat.purchase.line'
    _order = 'date'

    @api.one
    @api.depends('total_amount','vat_tax_id','municipal_tax_id','internal_tax_id','vat_percep_tax_id','gross_tax_id')
    def _compute_amount(self):
        tax = 1
        if self.vat_tax_id:
            tax += self.vat_tax_id.amount/100
        if self.municipal_tax_id:
            tax += self.municipal_tax_id.amount/100
        if self.internal_tax_id:
            tax += self.internal_tax_id.amount/100
        if self.vat_percep_tax_id:
            tax += self.vat_percep_tax_id.amount/100
        if self.gross_tax_id:
            tax += self.gross_tax_id.amount/100

        self.net_amount = self.total_amount / tax
        self.vat_amount = self.net_amount * self.vat_tax_id.amount/100
        self.municipal_amount = self.net_amount * self.municipal_tax_id.amount/100
        self.internal_amount = self.net_amount * self.internal_tax_id.amount/100
        self.vat_percep_amount = self.net_amount * self.vat_percep_tax_id.amount/100
        self.gross_amount = self.net_amount * self.gross_tax_id.amount/100

        

    date= fields.Date('Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    voucher_type_id = fields.Many2one('sigvat.voucher.type', 'Voucher Type', required=True, default=1)
    point_of_sale = fields.Integer(string="Point of Sale", required=True)
    voucher_number = fields.Integer(string="Voucher Number", required=True)
    total_amount = fields.Float(string="Total Amount", digits=(13, 2), required=True)
    # net_amount = fields.Float(string="Net Amount", digits=(13, 2), required=True)
    net_amount = fields.Float(string='Net Amount', digits=(13, 2),
        store=True, readonly=False, compute='_compute_amount')
    vat_tax_id = fields.Many2one('account.tax', 'Vat Tax', required=True)
    vat_amount = fields.Float(string="Vat Amount", digits=(13, 2), required=False)
    municipal_tax_id = fields.Many2one('account.tax', 'Municipal Tax', required=False)
    municipal_amount = fields.Float(string="Municipal Amount", digits=(13, 2), required=False)
    internal_tax_id = fields.Many2one('account.tax', 'Internal Tax', required=False)
    internal_amount = fields.Float(string="Internal Amount", digits=(13, 2), required=False)
    vat_percep_tax_id = fields.Many2one('account.tax', 'Vat Perception Tax', required=False)
    vat_percep_amount = fields.Float(string="Vat Perception Amount", digits=(13, 2), required=False)
    gross_tax_id = fields.Many2one('account.tax', 'Gross Income Tax', required=False)
    gross_amount = fields.Float(string="Gross Income Amount", digits=(13, 2), required=False)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    operation_code = fields.Selection( string="Operation Code",
        selection=[
            ('0', '0 - No corresponde'),
            ('A', 'A - No Alcanzado'),
            ('C', 'C - Operaciones de Canje'),
            ('E', 'E - Operaciones exentas'),
            ('N', 'N - No gravado'),
            ('T', 'T - Reintegro Decreto 1043/2016'),
            ('X', 'X - Importación/Exportación Exterior'),
            ('Z', 'Z - Importación/Exportación Zona Franca'),
            ], required=True, default='0')
    journal_id = fields.Many2one('sigvat.journal', 'Vat Journal')

    @api.onchange('partner_id')
    def on_change_cuit(self):
        self.cuit = self.partner_id.cuit

    @api.constrains('auto_confirm')
    def _check_pos(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.point_of_sale == 0:
                return False
        return True

    @api.constrains('auto_confirm')
    def _check_voucher_number(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.voucher_number == 0:
                return False
        return True

    @api.constrains('auto_confirm')
    def _check_date(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            month = int(line.journal_id.month)
            year = int(line.journal_id.year.name)
            from_date = str(datetime(year, month, 1))[0:10]
            last_day = calendar.monthrange(year,month)
            to_date = str(datetime(year, month, last_day[1]))[0:10]

            if line.date < from_date or line.date > to_date:
                raise exceptions.Warning(_("La fecha %s no pertenece al periodo %s/%s."%(line.date,month,year)))
        return True

    _constraints = [
        (_check_pos, 'Point of sale must be diferent than zero.', []),
        (_check_voucher_number, 'Voucher number must be diferent than zero.', []),
        (_check_date, 'La fecha no pertenece al periodo.', []),
    ]

class SigVatSaleLine(models.Model):

    _inherit= 'sigvat.purchase.line'
    _name= 'sigvat.sale.line'

class AccountTax(models.Model):

    _inherit= 'account.tax'
    _name= 'account.tax'
    type_tax = fields.Selection( string="Type Tax",
        selection=[
            ('vat', 'Value Added Tax'),
            ('vat_percep', 'Value Added Tax Perception'),
            ('municipal', 'Municipal'),
            ('internal', 'Internal'),
            ('gross', 'Gross Income'),
            ])

    @api.model
    def _auto_init(self):
        res = super(AccountTax, self)._auto_init()
        self.env.cr.execute("""
            update account_tax set type_tax='vat' where description in ('ITAX_21-OUT','OTAX_21-IN','ITAX_27-OUT','OTAX_27-IN','ITAX_105-OUT','OTAX_105-IN');
            update account_tax set type_tax='vat_percep' where description in ('OTAX_02-IN');
        """)
        return res

class ResCurrency(models.Model):

    _inherit= 'res.currency'
    code = fields.Char(size=3,string= "Code")

    @api.model
    def _auto_init(self):
        res = super(ResCurrency, self)._auto_init()
        self.env.cr.execute("""
            update res_currency set code = 'PES' where name='ARS';
            update res_currency set code = 'DOL' where name='USD';
            update res_currency set active = false where name='EUR';
        """)
        return res
    
    
    


