# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Desarrollado por Soltic S.R.L., quien ostenta los derechos de Copyright
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

from openerp import models, fields, api, _
import amount_to_text_es
from openerp.tools.float_utils import float_round
import math

MONTH = {1 : 'Enero',
        2 : 'Febrero',
        3 : 'Marzo',
        4 : 'Abril',
        5 : 'Mayo',
        6 : 'Junio',
        7 : 'Julio',
        8 : 'Agosto',
        9 : 'Septiembre',
        10 : 'Octubre',
        11 : 'Noviembre',
        12 : 'Diciembre',}


class SigVatPayroll(models.Model):

    _name= 'sigvat.payroll'

    def _get_year(self):
        try:
            self.year = str(self.date[0:4])
        except:
            pass

    def get_month(self):
        return MONTH[int(self.month)]

    def get_month_date(self):
        return MONTH[int(self.date[5:7])]

    @api.multi
    def generate_note(self):
        text = self.get_amount_in_words()
        self.notes = _("""Recibí de %s la suma de Pesos: %s en concepto de mis haberes correspondiente al período arriba indicado y conforme a la presente liquidación dejando constancia de haber recibido un duplicado de este recibo.""")%(self.employeer_id.name,text)

    @api.one
    @api.depends('line_ids.amount')
    def _compute_amount(self):
        for line in self.line_ids:
            if line.concept_id.type_id.code in ['HRE','HNR']:
                self.total_gross += line.amount
                if line.concept_id.type_id.code in ['HRE']:
                    self.total_hre += line.amount
                if line.concept_id.type_id.code in ['HNR']:
                    self.total_hnr += line.amount
            else:
                self.total_deduction += line.amount
        self.total_amount = self.total_gross - self.total_deduction


    @api.onchange('total_amount')
    def _onchange_amount(self):
        self.amount_in_words = self.get_amount_in_words()

    @api.multi
    def get_amount_in_words(self):
        amount_in_words = amount_to_text_es.amount_to_text(math.floor(self.total_amount), lang='es', currency='')
        amount_in_words = amount_in_words.replace(' and Zero Cent', '') # Ugh
        decimals = self.total_amount % 1
        if decimals >= 10**-2:
            amount_in_words += _(' and %s/100') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return amount_in_words

    employeer_id = fields.Many2one('res.partner', 'Employeer', domain="[('is_employeer','=','True')]", required=True)
    beneficiary_id = fields.Many2one('res.partner', 'Beneficiary',domain="[('is_beneficiary','=','True')]", required=True)
    date = fields.Date('Date', required=True)
    month = fields.Selection(default='01', string="Month", required=True,
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
    year = fields.Char(compute="_get_year", string="Year")
    last_deposited_month = fields.Selection(string="Last Deposited Month", 
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
    last_deposited_year = fields.Char(size=4, string="Last Deposited Year")
    line_ids = fields.One2many('sigvat.payroll.line', 'payroll_id', string='Payroll Lines', copy=True)
    total_gross = fields.Float(string='Total Gross',
        store=True, readonly=True, compute='_compute_amount')
    total_deduction = fields.Float(string='Total Deduction',
        store=True, readonly=True, compute='_compute_amount')
    total_amount = fields.Float(string='Total Amount',
        store=True, readonly=True, compute='_compute_amount')
    total_hre = fields.Float(string='Total HRE',
        store=True, readonly=True, compute='_compute_amount')
    total_hnr = fields.Float(string='Total HNR',
        store=True, readonly=True, compute='_compute_amount')
    notes = fields.Text('Notes')
    observations = fields.Text('Observaciones')
    amount_in_words = fields.Char(string="Amount in Words", readonly=True)

class SigVatPayrollLine(models.Model):

    _name= 'sigvat.payroll.line'

    concept_id = fields.Many2one('sigvat.payroll.concept', 'Concept', required=True)
    payroll_id = fields.Many2one('sigvat.payroll', 'Payroll', required=True)
    amount = fields.Float('Amount', required=True)
    sequence = fields.Integer(related='concept_id.sequence', readonly=True)
    type_id = fields.Many2one('sigvat.payroll.concept.type', related='concept_id.type_id', string='Concept Type', readonly=True)
    employeer_id = fields.Many2one('res.partner', related='payroll_id.employeer_id', string='Employer', readonly=True)
    beneficiary_id = fields.Many2one('res.partner', related='payroll_id.beneficiary_id', string='Beneficiary', readonly=True)
    
    _sql_constraints = [
        ('line_uniq', 'UNIQUE (concept_id,payroll_id)',  'The Line already exists'),
    ]



class SigVatPayrollCategory(models.Model):

    _name= 'sigvat.payroll.category'

    name = fields.Char(string='Name', required=True, size=64)
    code = fields.Char(string='Code', required=True, size=12)
    description = fields.Text(string='Description', size=180)
    active = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'The name already exists'),
        ('code_uniq', 'UNIQUE (code)',  'The code already exists'),
    ]

class SigVatPayrollConceptType(models.Model):

    _name= 'sigvat.payroll.concept.type'

    name = fields.Char(string='Name', required=True, size=64)
    code = fields.Char(string='Code', required=True, size=12)
    description = fields.Text(string='Description', size=180)
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'The name already exists'),
        ('code_uniq', 'UNIQUE (code)',  'The code already exists'),
    ]

class SigVatPayrollConcept(models.Model):

    _name= 'sigvat.payroll.concept'

    name = fields.Char(string='Name', required=True, size=64)
    code = fields.Char(string='Code', required=True, size=12)
    description = fields.Text(string='Description', size=180)
    active = fields.Boolean('Active', default=True)
    type_id = fields.Many2one('sigvat.payroll.concept.type', 'Concept Type', required=True)
    sequence = fields.Integer('Sequence', required=True)
    
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',  'The name already exists'),
        ('code_uniq', 'UNIQUE (code)',  'The code already exists'),
        ('sequence_uniq', 'UNIQUE (sequence)',  'The sequence already exists'),
    ]

   