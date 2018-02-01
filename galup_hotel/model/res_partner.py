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
import time
from openerp.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, UserError, ValidationError


class HotelDiscount(models.Model):

    _name = 'hotel.discount'

    name = fields.Char('Nombre', required=True)
    discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)


class res_partner(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'
    # _rec_name = 'name'

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
    hotelfolio_ids = fields.One2many('hotel.folio', 'partner_id', 'Folios')
    

    _defaults = {
        'is_company': False,
        'customer': False,
    }

    _sql_constraints = [
        ('identification_id_uniq', 'UNIQUE (identification_id)',  'El número de identificación debe ser único'),
    ]

    # Método name_get sobrescrito para que se muestre en el campo Huesped el nombre + DNI + cantidad de visitas
    def name_get(self, cr, uid, ids, context=None):
    	res = []
    	partners = self.browse(cr, uid, ids, context)
    	for partner in partners:
    		name =str(partner.name)
    		dni = str(partner.main_id_number)
    		cant = fields.Integer()
    		cant = 0
    		for f in partner.hotelfolio_ids:
    			cant = 1 + cant
    		visit = str(cant)
    		tit = name + ' (DNI: ' + dni + ', ' ' Visitas: ' + visit + ') '
        	res.append((partner.id, tit))
    	return res

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
    early_checkin = fields.Boolean('Early Checkin')
    late_checkout = fields.Boolean('Late Checkin')
    early_checkin_hour = fields.Integer('Hora Early Checkin', required=False, default=lambda *a: 0)
    late_checkout_hour = fields.Integer('Hora Late Checkout', required=False, default=lambda *a: 11)
    check_applied = fields.Boolean('Check applied', default=lambda *a: False)
    debt_status = fields.Selection(string='Estado de deuda', related='hotel_invoice_id.state')

    @api.multi
    def calculate_check(self):
        if not self.early_checkin and not self.late_checkout:
            raise ValidationError(_('Debe seleccionar la opción de early checkin y/o late checkout'))
        if self.early_checkin_hour < 0 or self.early_checkin_hour > 11:
            raise ValidationError(_('El early checkin debe ser entre las 0 y 11 hs.'))
        if self.late_checkout_hour < 11 or self.late_checkout_hour > 24:
            raise ValidationError(_('El late checkout debe ser entre las 11 y 24 hs.'))
        tax_obj = self.env['account.tax']
        for line in self.room_lines:
            tax_ids = line.tax_id.ids
            if self.early_checkin:
                tax_id = tax_obj.search([('check_type', '=', 'early'),('hour_from', '<=', self.early_checkin_hour),('hour_to', '>=', self.early_checkin_hour)])
                tax_ids.append(tax_id.id)
            if self.late_checkout:
                tax_id = tax_obj.search([('check_type', '=', 'late'),('hour_from', '<=', self.late_checkout_hour),('hour_to', '>=', self.late_checkout_hour)])
                tax_ids.append(tax_id.id)
            line.tax_id = tax_ids
        self.write({'check_applied': True})

    @api.multi
    def uncalculate_check(self):
        tax_obj = self.env['account.tax']
        for line in self.room_lines:
            tax_ids = line.tax_id.ids
            if self.early_checkin:
                tax_id = tax_obj.search([('check_type', '=', 'early'),('hour_from', '<=', self.early_checkin_hour),('hour_to', '>=', self.early_checkin_hour)])
                tax_ids.remove(tax_id.id)
            if self.late_checkout:
                tax_id = tax_obj.search([('check_type', '=', 'late'),('hour_from', '<=', self.late_checkout_hour),('hour_to', '>=', self.late_checkout_hour)])
                tax_ids.remove(tax_id.id)
            line.tax_id = [(6, 0, tax_ids)]
        self.write({'check_applied': False})

class HotelFolioLine(models.Model):

    _inherit = 'hotel.folio.line'

    @api.onchange('discount_id')
    def discount_id_change(self):
        if self.discount_id:
            self.discount = self.discount_id.discount

    discount_id = fields.Many2one('hotel.discount', 'Descuento')

class HotelRoom(models.Model):

    _inherit = 'hotel.room'    

    status = fields.Selection([('available', 'Available'),
                               ('occupied', 'Occupied'),
                               ('blocked', 'Bloqueado'),
                               ],
                              'Status', default='available')
    
    issue_lines = fields.One2many('hotel.room.issue', 'room_id',help="Incidencias.")

    @api.multi
    def CloseIssue(self):
        issue_obj = self.env['hotel.room.issue']
        room_obj = self.env['hotel.room']
        issue_ids = issue_obj.search([('room_id','=',self.id),('close_date','=',False)])
        for issue in issue_ids:
            issue.close_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.status = 'available'
        self.isroom = True
        return True

class FolioRoomLine(models.Model):

    _inherit = 'folio.room.line'
    debt_status = fields.Selection(string='Estado de deuda', related='folio_id.debt_status')
    

class HotelRoomIssue(models.Model):

    _name = 'hotel.room.issue'

    name = fields.Char('Descripcion', required=True)
    room_id = fields.Many2one('hotel.room', string='Habitación',
                               ondelete='cascade')    
    issue_date = fields.Datetime('Fecha de la incidencia', required=True,
                                          default=(lambda *a:
                                          time.strftime
                                          (DEFAULT_SERVER_DATETIME_FORMAT)))
    close_date = fields.Datetime('Fecha de resolucion', required=False)

class AccountTax(models.Model):
    _inherit = 'account.tax'    

    # early checkin / late checkout

    check_type = fields.Selection([('early', 'Early Checkin'),
                               ('late', 'Late Check Out'),
                               ],
                              'Tipo de checkin/checkout')
    hour_from = fields.Integer('Hora Desde', required=False)
    hour_to = fields.Integer('Hora Hasta', required=False)

