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
        room_id = self._context['active_ids'][0]
        wizard = self.read(['name'])[0]
        issue_obj.create({'name': wizard['name'],
                          'room_id': room_id})
        room = room_obj.browse(room_id)
        room.status = 'blocked'
        room.isroom = False
        return True
