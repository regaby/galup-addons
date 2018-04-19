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
from openerp.exceptions import except_orm, ValidationError


class MakeInvoiceWizard(models.TransientModel):

    _name = 'wizard.make.invoice'

    grouped = fields.Boolean('Group the Folios')

    @api.multi
    def makeInvoices(self):
        ctx = self.env.context.copy()
        order_obj = self.env['hotel.folio']
        invoice_obj = self.env['account.invoice']
        newinv = []
        for order in order_obj.browse(self._context['active_ids']):
            if order.state not in ['done'] or order.invoice_status not in ['to invoice']:
                raise ValidationError(_('El folio %s no está en estado "Checkout Realizado" y/o estado de factura "Para Facturar"')%(order.name))

        active_ids = self._context['active_ids']
        invoice_ids = []
        for a_id in active_ids:
            ctx.update({'active_ids': [a_id],
                        })
            make_invoice = self.with_context(ctx).env['sale.advance.payment.inv']
            # make_invoice.advance_payment_method='all'
            make_invoice_id = make_invoice.create({'advance_payment_method':'all'})
            hotel = order_obj.browse(a_id)
            res_id = invoice_obj.search([('origin','ilike',hotel.name)])
            if hotel and res_id:
                invoice_ids.append(res_id.id)
        if self._context.get('open_invoices', False):
            return {
                'domain': "[('id','in', [" + ','.join(map(str, invoice_ids)) + "])]",
                'name': 'Facturas',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'view_id': False,
                'type': 'ir.actions.act_window'
            }
        return {'type': 'ir.actions.act_window_close'}
            
            
        
