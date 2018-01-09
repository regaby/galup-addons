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
from datetime import datetime
from dateutil import relativedelta
import openerp.addons.decimal_precision as dp


class HotelDiscount(models.Model):

    _name = 'hotel.discount'

    name = fields.Char('Nombre', required=True)
    discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)


class res_partner(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'

    # _partner_age_fnt = lambda self, cr, uid, ids, name, arg, context={}: self._partner_age(cr, uid, ids, name, arg, context)

    @api.one
    @api.depends('birthday')
    def _partner_age_fnt(self):
        def compute_age_from_dates (partner_dob, patient_deceased=False, patient_dod=False):
            now = datetime.now()
            if (partner_dob):
                dob = datetime.strptime(partner_dob, '%Y-%m-%d')
                if patient_deceased :
                    dod = datetime.strptime(patient_dod, '%Y-%m-%d %H:%M:%S')
                    delta = relativedelta.relativedelta(dod, dob)
                    deceased = " (deceased)"
                else:
                    delta = relativedelta.relativedelta(now, dob)
                    deceased = ''
                years_months_days = str(delta.years)
            else:
                years_months_days = "Fecha de nacimiento no asignada !"

            return years_months_days
        result = {}
        # for partner_data in self.browse(cr, uid, ids, context=context):
        partner_data = self
        self.age= compute_age_from_dates (partner_data.birthday)
 
    identification_id = fields.Char(size=20,string="Nro. Documento",help="DNI/CPF/Pasaporte/Travel document")
    job_id = fields.Many2one('hr.job', 'Ocupación/Profesión')
    birthday = fields.Date('Fecha de nacimiento')
    gender = fields.Selection([('male', 'Hombre'), ('female', 'Mujer'), ('other', 'Otro')], string='Género')
    marital = fields.Selection([('single', 'Soltero/a'), ('married', 'Casado/a'), ('widower', 'Viudo/a'), ('divorced', 'Divorciado/a')], string='Estado civil')
    smoker = fields.Boolean(string="Fumador")
    regular_passenger = fields.Boolean(string="Pasajero Frecuente")
    is_passenger = fields.Boolean()
    nationality_id = fields.Many2one('res.country', 'Nacionalidad (País)')
    # 'age' : fields.function(_partner_age_fnt, method=True, type='char', size=32, string='Patient Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
    age = fields.Char(string='Edad', 
        store=False, readonly=False, compute='_partner_age_fnt')
    observations = fields.Text('Observaciones')
    has_car = fields.Boolean(string="Tiene vehiculo")
    discount_id = fields.Many2one('hotel.discount', 'Descuento')

    _defaults = {
        'is_company': False,
        'customer': False,
    }

    _sql_constraints = [
        ('identification_id_uniq', 'UNIQUE (identification_id)',  'El número de identificación debe ser único'),
    ]

class Guest(models.Model):

    _name = 'hotel.guest'

    name = fields.Char('Nombre', required=True)
    last_name = fields.Char('Apellido', required=True)
    identification_id = fields.Char(size=20,string="Nro. Documento",help="DNI/CPF/Pasaporte/Travel document", required=True)
    folio_id = fields.Many2one('hotel.folio', string='Folio',
                               ondelete='cascade')

class HotelFolio(models.Model):

    _name = 'hotel.folio'
    _inherit = 'hotel.folio'

    guest_lines = fields.One2many('hotel.guest', 'folio_id',
                                 readonly=True,
                                 states={'draft': [('readonly', False)],
                                         'sent': [('readonly', False)]},
                                 help="Acompañantes.")

class HotelFolioLine(models.Model):

    _inherit = 'hotel.folio.line'

    @api.onchange('discount_id')
    def discount_id_change(self):
        if self.discount_id:
            self.discount = self.discount_id.discount

    discount_id = fields.Many2one('hotel.discount', 'Descuento')
