# -*- coding: utf-8 -*-
from openerp import models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def payment_print_recibo_x(self):
        self.ensure_one()
        # if we print caming from other model then active id and active model
        # is wrong and it raise an error with custom filename
        self = self.with_context(
            active_model=self._name, active_id=self.id, active_ids=self.ids)
        report_obj = self.env['ir.actions.report.xml']
        # report_name = report_obj.get_report_name(self._name, self.ids)
        report_name = 'recibo_x_promover'
        print 'report_name',report_name
        return self.env['report'].get_action(self, report_name)


