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




class res_partner(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'

    main_id_number = fields.Char('numero', store=False, required=False)
    main_id_category_id = fields.Many2one('res.partner.id_category', required=False)

    def _get_default_category(self, cr, uid, context=None):
        res = self.pool.get('res.partner.id_category').search(cr, uid, [('code','=','CUIT')], context=context)
        return res and res[0] or False

    _defaults = {
        'main_id_number' : 0,
        'main_id_category_id' : _get_default_category,
    }


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
            raise ValidationError(_('El número de identificación debe ser único. Actualmente existe para %s')%(demo_record.partner_id.name))
            return False
        return True

    _constraints = [(_check_dni,"El número de identificación debe ser único",[])]


class ResPartnerIdNumberCategory(models.Model):
    _name = "res.partner.id_category"
    _inherit = "res.partner.id_category"
    afip_code = fields.Integer(default = 99, readonly=True)
