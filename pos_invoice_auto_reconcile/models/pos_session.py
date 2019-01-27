# -*- coding: utf-8 -*-
# from openerp import models, fields
# from openerp.tools import float_is_zero
# from openerp.exceptions import UserError, ValidationError
# import time
from openerp.tools.translate import _
from openerp.osv import fields, osv
# import logging_logger = logging.getLogger(__name__)

class pos_session(osv.osv):
    _inherit = 'pos.session'

    def _confirm_orders(self, cr, uid, ids, context=None):

        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        pos_order_obj = self.pool.get('pos.order')
        for session in self.browse(cr, uid, ids, context=context):
            local_context = dict(context or {}, force_company=session.config_id.journal_id.company_id.id)
            order_ids = [order.id for order in session.order_ids if order.state == 'paid']

            move_id = account_move_obj.create(cr, uid, {'ref' : session.name, 'journal_id' : session.config_id.journal_id.id, }, context=local_context)

            pos_order_obj._create_account_move_line(cr, uid, order_ids, session, move_id, context=local_context)

            for order in session.order_ids:
                if order.state == 'done':
                    continue
                if order.state not in ('paid', 'invoiced'):
                    raise osv.except_osv(
                        _('Error!'),
                        _("You cannot confirm all orders of this session, because they have not the 'paid' status"))
                else:
                    pos_order_obj.signal_workflow(cr, uid, [order.id], 'done')
            order_ids = self.pool.get('pos.order').search(cr, uid, [('session_id','=', session.id)])
            for obj_order_id in self.pool.get('pos.order').browse(cr, uid, order_ids, context=context):
                move_line = []

                print '\n\n\nobj_order_id.invoice_id.move_id', obj_order_id.invoice_id.move_id
                for move_line_id in obj_order_id.invoice_id.move_id.line_ids:
                    if move_line_id.name == obj_order_id.name:

                        move_line.append(move_line_id.id)


                for statement_id in obj_order_id.statement_ids:
                    move_line_ids = account_move_line_obj.search(cr, uid, [('statement_id','=', statement_id.statement_id and statement_id.statement_id.id)])

                    for line in account_move_line_obj.browse(cr, uid, move_line_ids):

                        if line.credit and line.name.strip().strip(':') == obj_order_id.name:
                          move_line.append(line.id)

                ctx = context.copy()
                ctx.update({'active_ids': move_line})
                self.pool.get('account.move.line.reconcile').trans_rec_reconcile_full(cr, uid, [], ctx)
                #move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('name','=',obj_order_id.name)])
                #print "@######move_line_id@@@@", move_line_ids

        return True
