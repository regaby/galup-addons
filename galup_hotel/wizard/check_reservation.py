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

class CheckReservationWizard(models.TransientModel):

    _name = 'check.reservation.wizard'

    name = fields.Char('Descripcion', required=True)
    reservas = fields.Text('Reservas', required=True)
    room_id = fields.Many2one('hotel.room','Room')

    @api.multi
    def CheckReservationAction(self):
        room_obj = self.env['hotel.room']
        wizard = self.read(['name','room_id'])[0]
        room = room_obj.browse(wizard['room_id'][0])
        room.makeIssue(wizard['name'],wizard['room_id'][0])
        return {'type': 'ir.actions.act_window_close'}
