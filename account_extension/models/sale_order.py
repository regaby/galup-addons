# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
# from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    vat_discriminated = fields.Boolean(
        compute='_compute_vat_discriminated')

    @api.one
    @api.depends(
        'partner_id',
        'partner_id.afip_responsability_type_id',
        'company_id',
        'company_id.partner_id.afip_responsability_type_id',)
    def _compute_vat_discriminated(self):
        self.vat_discriminated = False
