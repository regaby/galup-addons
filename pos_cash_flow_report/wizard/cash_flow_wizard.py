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

class CashFlowWizard(models.TransientModel):

    _name = 'pos.cash.flow.wizard'

    date_start = fields.Date('Date Start', required=True, default=fields.Date.context_today)
    date_end = fields.Date('Date End', required=True, default=fields.Date.context_today)
    journal_ids = fields.Many2many('account.journal', 'pos_cash_flow_journals_rel', 'journal_id',
                                   'wizard_id', 'Journals')

    @api.multi
    def print_report(self):
        form = self.read(['date_start', 'date_end', 'journal_ids'])[0]
        datas = {
            'id': self.id,
            'ids': self.ids,
            'model': 'pos.cash.flow.wizard',
            'form': form
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pos.cash.flow.report',
            'datas': datas,
            }
