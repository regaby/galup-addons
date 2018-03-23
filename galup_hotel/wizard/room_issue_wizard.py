# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# ---------------------------------------------------------------------------

from openerp import models, fields, api
import time
from openerp.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT

class RoomIssueWizard(models.TransientModel):

    _name = 'room.issue.wizard'

    name = fields.Char('Descripcion', required=True)

    @api.multi
    def makeIssue(self):
        issue_obj = self.env['hotel.room.issue']
        room_obj = self.env['hotel.room']
        reservation_obj = self.env['hotel.room.reservation.line']
        room_id = self._context['active_ids'][0]
        wizard = self.read(['name'])[0]
        reservation_ids = reservation_obj.search([('check_in','>',time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),('state','=','assigned'),('room_id','=',room_id)])
        if reservation_ids:
            msg=''
            for r in reservation_ids:
                msg += 'Reserva: %s\n'%r.reservation_id.reservation_no
                msg += 'Huesped: %s\n'%r.reservation_id.partner_id.name
                msg += 'Checkin: %s\n'%r.check_in
                msg += 'Checkout: %s\n'%r.check_out
                msg += '--------------------------------------------\n'
            msg += '¿Desea bloquear de todas formas?'
            # dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'galup_hotel', 'check_reservation_wizard_form_view')
            dummy, view_id = self.env['ir.model.data'].get_object_reference('galup_hotel', 'check_reservation_wizard_form_view')
            return {
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'check.reservation.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'views': [(view_id, 'form')],
                'context': {'active_ids': self.id,'default_name':wizard['name'],'default_reservas': msg,'default_room_id': room_id},               
            }
        else:
            room = room_obj.browse(room_id)
            room.makeIssue(wizard['name'],room_id)

