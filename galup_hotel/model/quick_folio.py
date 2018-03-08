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


class QuickFolio(models.TransientModel):
    _name = 'quick.folio'
    _description = 'Quick Folio'

    
    room_id = fields.Many2one('hotel.room', 'Habitación', required=True)
    partner_id = fields.Many2one('res.partner', string="Huesped",
                                 required=True)
    checkin = fields.Datetime('Check In', required=False)
    checkout = fields.Datetime('Check Out', required=False)
    observations = fields.Text('Observaciones')
    folio_id = fields.Many2one('hotel.folio', 'Folio')
    

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(QuickFolio, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'room_id' in keys:
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
                folio_room_obj = self.env['folio.room.line']
                folio_obj = self.env['hotel.folio']
                date = self._context['date'][0:10]
                cin = date+' 23:59:59'
                cout = date+' 00:00:00'
                folio_id = folio_room_obj.search([('room_id','=',int(roomid)),('check_in','<=',cin),('check_out','>=',cout)],order="check_out desc",limit=1)
                if folio_id:
                    folio = folio_obj.browse(folio_id.folio_id.id)
                    res.update({'partner_id': folio.partner_id.id,
                        'checkin':folio.checkin_date,
                        'checkout':folio.checkout_date,
                        'observations':folio.observations,
                        'folio_id': folio.id,
                        })

        return res

   