# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from openerp.osv import fields,osv
from openerp import tools

class purchase_report(osv.osv):
    _inherit = "purchase.report"
    _order = 'quantity desc'
