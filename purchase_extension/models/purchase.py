from openerp import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='Nueva')