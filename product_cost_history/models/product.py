# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import except_orm, UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    history_ids = fields.One2many('product.price.history','product_id','History')

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    

    @api.multi
    def _add_supplier_to_product(self):
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
            supplierinfo = {
                'name': partner.id,
                'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                'product_uom': line.product_uom.id,
                'min_qty': 0.0,
                'price': self.currency_id.compute(line.price_unit, currency),
                'currency_id': currency.id,
                'delay': 0,
            }
            vals = {
                'seller_ids': [(0, 0, supplierinfo)],
                'standard_price' : self.currency_id.compute(line.price_unit, currency),
            }
            if line.product_id.lst_price < line.price_unit:
                raise UserError('El precio de venta es menor que el precio de compra del producto: %s'%(line.product_id.name))
            try:
                line.product_id.write(vals)
            except AccessError:  # no write access rights -> just ignore
                break

