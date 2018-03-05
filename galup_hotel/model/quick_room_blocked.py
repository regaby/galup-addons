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


class QuickRoomBlocked(models.TransientModel):
    _name = 'quick.room.blocked'
    _description = 'Quick Room Blocked'

    
    room_id = fields.Many2one('hotel.room', 'Habitación', required=True)
    name = fields.Char('Descripción', required=True)
    issue_date = fields.Datetime('Fecha de la incidencia', required=True)
    

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
        res = super(QuickRoomBlocked, self).default_get(fields)
        if self._context:
            keys = self._context.keys()
            if 'date' in keys:
                date_out = datetime.datetime.strptime(self._context['date'][0:10], '%Y-%m-%d') + datetime.timedelta(days=1)
                res.update({
                    'check_in': self._context['date'],
                    'checkin_date': self._context['date'][0:10],
                    'checkout_date': str(date_out)[0:10],
                })
            if 'room_id' in keys:
                roomid = self._context['room_id']
                res.update({'room_id': int(roomid)})
                room_issue_obj = self.env['hotel.room.issue']
                issue_id = room_issue_obj.search([('room_id','=',int(roomid)),('close_date','=',False)])
                if issue_id:
                    issue = room_issue_obj.browse(issue_id.id)
                    res.update({'name': issue.name,'issue_date':issue.issue_date})

        return res

   