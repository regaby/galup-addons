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
import re


class HotelDiscount(models.Model):

    def name_get(self, cr, uid, ids, context=None):
        res = []
        discounts = self.browse(cr, uid, ids, context)
        for disc in discounts:
            tit = '%s (%d'%(disc.name,disc.discount)
            tit=tit+"%)"
            res.append((disc.id, tit))
        return res

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
 
    #identification_id = fields.Char(size=20,string="Nro. Documento",help="DNI/CPF/Pasaporte/Travel document")
    job_id = fields.Many2one('hr.job', 'Ocupación/Profesión')
    birthday = fields.Date('Fecha de nacimiento')
    gender = fields.Selection([('male', 'Hombre'), ('female', 'Mujer'), ('other', 'Otro')], string='Género')
    marital = fields.Selection([('single', 'Soltero/a'), ('married', 'Casado/a'), ('widower', 'Viudo/a'), ('divorced', 'Divorciado/a')], string='Estado civil')
    smoker = fields.Boolean(string="¿Es fumador?")
    regular_passenger = fields.Boolean(string="Pasajero Frecuente")
    is_passenger = fields.Boolean()
    unwelcome_guest = fields.Boolean(string="Huesped no grato")
    nationality_id = fields.Many2one('res.country', 'Nacionalidad (País)')
    # 'age' : fields.function(_partner_age_fnt, method=True, type='char', size=32, string='Patient Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
    age = fields.Char(string='Edad', 
        store=False, readonly=False, compute='_partner_age_fnt')
    observations = fields.Text('Observaciones')
    has_car = fields.Boolean(string="¿Tiene vehiculo?", default=False)
    discount_id = fields.Many2one('hotel.discount', 'Descuento')
    hotelfolio_ids = fields.One2many('hotel.folio', 'partner_id', 'Folios')
    main_id_number = fields.Char('numero', store=False)


    @api.onchange('country_id')
    def on_change_nationality(self):
        self.nationality_id = self.country_id

    def _get_default_category(self, cr, uid, context=None):
        res = self.pool.get('res.partner.id_category').search(cr, uid, [('code','=','DNI')], context=context)
        return res and res[0] or False

    _defaults = {
        'is_company': False,
        'customer': False,
        'main_id_number' : 0,
        'main_id_category_id' : _get_default_category,
        
    }


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

class ResPartnerIdNumber(models.Model):
    _name = "res.partner.id_number"
    _inherit = "res.partner.id_number"

    @api.constrains('auto_confirm')
    def _check_dni(self,cr,uid,ids,context=None):
        demo_record = self.browse(cr,uid,ids,context=context)[0]
        partner_ids = self.search(cr, uid, [('category_id','=',demo_record.category_id.id),('name','=',demo_record.name),('active','=',True)])
        partner_ids.remove(ids[0])
        if len(partner_ids)>0:
            demo_record = self.browse(cr,uid,partner_ids,context=context)[0]
            raise ValidationError(_('El número de identificación del huésped debe ser único. Actualmente existe para %s')%(demo_record.partner_id.name))
            return False
        return True
        
    _constraints = [(_check_dni,"El número de identificación del huésped debe ser único",[])]
    # _sql_constraints = [
    #     ('partner_id_number_uniq', 'UNIQUE (category_id,name)',  'El número de identificación del huésped debe ser único'),
    # ]


class ResPartnerIdNumberCategory(models.Model):
    _name = "res.partner.id_category"
    _inherit = "res.partner.id_category"
    afip_code = fields.Integer(default = 99, readonly=True)

class ResCountryEstate(models.Model):
    _name = "res.country.state"
    _inherit = "res.country.state"
    
    code = fields.Char(required=False) 

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
                                 help="Acompañantes.")
    early_checkin = fields.Boolean('Early Checkin')
    late_checkout = fields.Boolean('Late Checkout')
    early_checkin_hour = fields.Integer('Hora Early Checkin', required=False, default=lambda *a: 0)
    late_checkout_hour = fields.Integer('Hora Late Checkout', required=False, default=lambda *a: 11)
    check_applied = fields.Boolean('Check applied', default=lambda *a: False)
    invoice_state = fields.Selection(string='Estado de Factura', related='hotel_invoice_id.state')
    car_partner = fields.Boolean(string='¿Tiene vehículo?', related='partner_id.has_car')
    smoker_partner = fields.Boolean(String='¿Es Fumador?', related='partner_id.smoker') 
    regular_passenger = fields.Boolean(String='Pasajero Frecuente', related='partner_id.regular_passenger') 
    nacionality_partner = fields.Many2one('res.country', 'Nacionalidad' , related='partner_id.nationality_id', required=True)
    debt_status = fields.Selection([('debe', 'Debe'),
                               ('pagado', 'Pagado (Anotar en observaciones los detalles del pago)'),],
                              'Estado de Deuda', default='debe', required=True)
    unwelcome_guest = fields.Boolean(string='Huesped no grato', related='partner_id.unwelcome_guest')

    @api.onchange('country_partner')
    def on_change_nationality(self):
        self.nacionality_partner = self.country_partner

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

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for folio in self:
            if folio.state not in ['cancel']:
                raise ValidationError(_('Para poder eliminar el registro, el mismo debe estar en estado cancelado.'))
        return super(HotelFolio, self).unlink()

    def update_partner2(self, vals, partner):
        partner_obj = self.env['res.partner']
        partner = partner_obj.browse(partner)
        if 'smoker_partner' in vals:
            partner.write({'smoker': vals['smoker_partner']})
        if 'car_partner' in vals:
            partner.write({'has_car': vals['car_partner']})
        if 'nacionality_partner' in vals:
            partner.write({'nationality_id': vals['nacionality_partner']})

    @api.model
    def create(self, vals, check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio.
        """
        self.update_partner2(vals,vals['partner_id'])
        return super(HotelFolio, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        self.update_partner2(vals,self.partner_id.id)
        return super(HotelFolio, self).write(vals)

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

    @api.multi
    def makeIssue(self,name_issue,room_id):
        issue_obj = self.env['hotel.room.issue']
        issue_obj.create({'name': name_issue,
                          'room_id': room_id})
        self.status = 'blocked'
        self.isroom = False
        return True

class FolioRoomLine(models.Model):

    _inherit = 'folio.room.line'
    invoice_state = fields.Selection(string='Estado de Factura', related='folio_id.invoice_state')
    debt_status = fields.Selection(string='Estado de Factura', related='folio_id.debt_status')
    

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
    name = fields.Char(string='Nombre del gasto', required=True)

class HotelReservation(models.Model):

    _name = "hotel.reservation"
    _inherit = 'hotel.reservation'

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for reservation in self:
            if reservation.state not in ['cancel']:
                raise ValidationError(_('Para poder eliminar el registro, el mismo debe estar en estado cancelado.'))
        return super(HotelReservation, self).unlink()

    unwelcome_guest = fields.Boolean(string='Huesped no grato', related='partner_id.unwelcome_guest')

class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', ''),
        ('sale', 'Checkin Realizado'),
        ('done', 'Checkout Realizado'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

class AccountInvoice(models.Model):
    _name = "account.invoice"
    _inherit = "account.invoice"

    state = fields.Selection([
            ('draft','Factura en Borrador'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Factura Validada'),
            ('paid', 'Factura Pagada'),
            ('cancel', 'Cancelled'),], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' status is used the invoice does not have an invoice number.\n"
             " * The 'Open' status is used when user create invoice, an invoice number is generated. Its in open status till user does not pay invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

    @api.multi
    @api.depends('document_number', 'number')
    def _get_invoice_number(self):
        """ Funcion que calcula numero de punto de venta y numero de factura
        a partir del document number. Es utilizado principalmente por el modulo
        de vat ledger citi
        """
        # TODO mejorar estp y almacenar punto de venta y numero de factura por
        # separado, de hecho con esto hacer mas facil la carga de los
        # comprobantes de compra

        # decidimos obtener esto solamente para comprobantes con doc number
        for rec in self:
            str_number = rec.display_name or False
            if str_number:
                if rec.document_type_id.code in ['33', '99', '331', '332']:
                    point_of_sale = '0'
                    # leave only numbers and convert to integer
                    invoice_number = str_number
                # despachos de importacion
                elif rec.document_type_id.code == '66':
                    point_of_sale = '0'
                    invoice_number = '0'
                elif "-" in str_number:
                    splited_number = str_number.split('-')
                    invoice_number = splited_number.pop()
                    point_of_sale = splited_number.pop()
                elif "-" not in str_number and len(str_number) == 12:
                    point_of_sale = str_number[:4]
                    invoice_number = str_number[-8:]
                else:
                    raise ValidationError(_(
                        'Could not get invoice number and point of sale for '
                        'invoice id %i') % (rec.id))
                rec.invoice_number = int(
                    re.sub("[^0-9]", "", invoice_number))
                rec.point_of_sale_number = int(
                    re.sub("[^0-9]", "", point_of_sale))

class SaleAdvancePaymentInv(models.TransientModel):
    _name = "sale.advance.payment.inv"    
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_advance_payment_method(self):
        if self._count() == 1:
            sale_obj = self.env['sale.order']
            order = sale_obj.browse(self._context.get('active_ids'))[0]
            if all([line.product_id.invoice_policy == 'order' for line in order.order_line]) or order.invoice_count:
                return 'all'
        return 'delivered'

    advance_payment_method = fields.Selection([
        # ('delivered', 'Invoiceable lines'),
        ('all', 'Facturar lineas'),
        # ('percentage', 'Down payment (percentage)'),
        # ('fixed', 'Down payment (fixed amount)')
        ], string='What do you want to invoice?', default=_get_advance_payment_method, required=True)

class QuickRoomReservation(models.TransientModel):
    _name = 'quick.room.reservation'
    _inherit = 'quick.room.reservation'
    
    unwelcome_guest = fields.Boolean(string='Huesped no grato', related='partner_id.unwelcome_guest')
