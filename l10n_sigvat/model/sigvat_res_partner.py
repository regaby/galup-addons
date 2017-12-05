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

from openerp import models, fields, api, _


class sigvat_res_partner(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'
 
    cuit = fields.Char(required=True, size=13)
    sigvat_category_id = fields.Many2one('sigvat.payroll.category', 'Category')
    is_beneficiary = fields.Boolean()
    is_employeer = fields.Boolean()
    date_start = fields.Date()
    reference = fields.Char(size=20, string="Identification Number")
    document_type = fields.Selection(default='80', string="Document Type",required=True,
        selection=[
            ('80', 'CUIT'),
            ('86', 'CUIL'),
            ('99', 'Sin identificar/venta global diaria'),
            ('96', 'DNI'),])

    _defaults = {
        'is_company': False,
        'customer': False,
        'country_id': 'base.ar',
    }

    _sql_constraints = [
        ('cuit_uniq', 'UNIQUE (cuit)',  'The CUIT already exists'),
        ('reference_uniq', 'UNIQUE (reference)',  'The reference already exists'),
    ]

class sigvat_res_partner_title(models.Model):

    _name = 'res.partner.title'
    _inherit = 'res.partner.title'