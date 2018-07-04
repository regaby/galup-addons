# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from openerp import models, fields, api, exceptions, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp import tools


class HrAttendance(models.Model):
    _inherit = "hr.attendance"


    state = fields.Selection([('draft', 'Borrador'),
                               ('validated', 'Validado')],
                              'Estado', default='draft', readonly=True)
    user_id = fields.Many2one('res.users', string='Validado por', readonly=True)

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        for attendance in self:
            if attendance.state not in ['draft']:
                raise ValidationError(_('Solo puede eliminar un registro en estado Borrador'))
        return super(HrAttendance, self).unlink()

    @api.multi
    def validate_attendance(self):
        '''
        @param self: object pointer
        '''
        self.write({'state': 'validated','user_id': self.env.user.id})
        return True

    @api.multi
    def draft_attendance(self):
        '''
        @param self: object pointer
        '''
        self.write({'state': 'draft'})
        return True

    @api.multi
    def copy(self):
        raise exceptions.UserError(_('No se puede duplicar una asistencia.'))
