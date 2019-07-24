# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
import time
from datetime import timedelta, datetime

class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_objects':self._get_objects,
        })

    def _get_objects(self, objects, context=None):
        date_start = objects.date_start
        date_end = objects.date_end
        statement_line = self.pool.get('account.bank.statement.line')
        args = [('date', '>=', date_start), ('date', '<=', date_end)]
        if objects.journal_ids:
            args.append(('journal_id', 'in', objects.journal_ids.ids))
        sql = """select id
            from account_bank_statement_line
            where date >='%s'
            and date <='%s'
            order by date asc, pos_statement_id asc
        """
        self.cr.execute(sql%(date_start, date_end))
        statement_ids = [x[0] for x in self.cr.fetchall()]
        res = []
        balance = objects.start_balance
        vals = {
            'date': '',
            'order': '',
            'statement': 'Saldo Inicial',
            'journal': '',
            'partner': '',
            'amount': balance,
            'reference': '',
            'balance': balance,
            }
        res.append(vals)
        for line in statement_line.browse(self.cr, self.uid, statement_ids):
            reference = ''
            if line.journal_id.id == 10:
                if line.check_pay_date:
                    reference += 'Fecha: %s - '%(line.check_pay_date)
                if line.check_owner:
                    reference += 'Propietario: %s - '%(line.check_owner)
                if line.check_bank_id:
                    reference += 'Banco: %s - '%(line.check_bank_id.name)
                if line.check_owner_vat:
                    reference += 'CUIT: %s - '%(line.check_owner_vat)
                if line.check_number:
                    reference += 'Nro. Cheque: %s - '%(line.check_number)
                if line.check_bank_acc:
                    reference += 'Cuenta: %s - '%(line.check_bank_acc)
            if line.journal_id.id == 8 and line.amount <= 0:
                if line.reference:
                    reference += 'Referencia: %s - '%(line.reference)
                if line.check_number:
                    reference += 'Nro. Comprobante: %s - '%(line.check_number)
            if line.journal_id.id == 14:
                if line.check_bank_id:
                    reference += 'Banco: %s - '%(line.check_bank_id.name)
                if line.check_owner_vat:
                    reference += 'CUIT: %s - '%(line.check_owner_vat)
                if line.check_cbu:
                    reference += 'CBU: %s - '%(line.check_cbu)
            balance += line.amount
            vals = {
                'date': line.date,
                'order': line.pos_statement_id.name,
                'statement': line.statement_id.name,
                'journal': line.journal_id.name,
                'partner': line.pos_statement_id.partner_id.name,
                'amount': line.amount,
                'reference': reference,
                'balance': balance,
            }
            res.append(vals)
        return res



