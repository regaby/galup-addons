# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
# from zklib import zklib


class hr_employee(models.Model):
    _inherit = "hr.employee"

    def _attendance_access(self):
    	# print super(hr_employee, self)._attendance_access(cr, uid, ids, name, args, context)
        # this function field use to hide attendance button to singin/singout from menu
        visible = False
        return dict([(x, visible) for x in self.ids])

    emp_code = fields.Char('Código Reloj')
    category = fields.Char('Categoría Reloj')
    attendance_access = fields.Boolean(string='Attendance Access', store=False, readonly=False, compute='_attendance_access')


