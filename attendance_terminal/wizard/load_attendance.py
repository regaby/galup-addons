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

from openerp import models, fields, api, _
import time
from openerp.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from tempfile import TemporaryFile
from tempfile import mkstemp
import os
import base64
import cStringIO
import csv
from datetime import timedelta
from datetime import datetime

class LoadAttendance(models.TransientModel):

    _name = 'load.attendance'

    name = fields.Char('Descripcion', required=False)
    data = fields.Binary('Archivo Asistencias', required=True)
    info = fields.Text('Info')
    state = fields.Selection( ( ('choose','choose'), ('done','done') ) ,default="choose")

    @api.multi
    def load_attendance(self):
        employee_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']
        data = base64.b64decode(self.data)
        file_input = cStringIO.StringIO(data)
        file_input.seek(0)
        # location = self.location
        reader_info = []
        delimeter = '\t'
        msg=''
        reader = csv.reader(file_input, delimiter=delimeter,
                            lineterminator='\r\n')
        ACTION={
            'sign_in': 'Entrada',
            'sign_out': 'Salida',
        }
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        for line in reader_info:
            print line
            emp_id = employee_obj.search([('emp_code','=',int(line[0]))])
            if emp_id:
                attendance_id = attendance_obj.search([('name','=',line[1])])
                if not attendance_id:
                    if line[3]=='0':
                        action='sign_in'
                    else :
                        action='sign_out'
                    delta = timedelta(hours=3)
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
                    from_dt = datetime.strptime(line[1], DATETIME_FORMAT) + delta

                    vals = {'employee_id': emp_id.id,
                            'name': str(from_dt),
                            'action': action}
                    print vals
                    try:
                        attendance_obj.create(vals)
                    except Exception, e:
                        msg+="%s - Empleado: %s - Horario: %s - Acción: %s \n"%((str(e[0]),emp_id.name,line[1],ACTION[action]))



        self.state='done'
        msg+='ok!!'
        self.info=msg
        view_id = self.env['ir.ui.view'].search([('model','=','load.attendance')])
        print view_id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'load.attendance',
            'name': _('Cargar Asistencias'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
             'nodestroy': True,
             'context': {}
                }