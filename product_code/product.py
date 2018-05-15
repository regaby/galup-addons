# -*- coding: utf-8 -*-
from openerp import api, fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"

    code = fields.Char(size=4)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_default_product_code(self, code):
        return self.env['ir.sequence'].get(code)

    @api.model
    def create(self, vals):
        print vals
        print vals
        print vals
        if 'product_tmpl_id' in vals:
            tmp = self.env['product.template'].browse(vals['product_tmpl_id'])
            code = tmp.categ_id.code
        if 'categ_id' in vals:
            categ_id = self.env['product.category'].browse(vals['categ_id'])
            code = categ_id.code
        vals['product_code'] = self._get_default_product_code(code)
        return super(ProductProduct, self).create(vals)

    product_code = fields.Char(index=True, help='Product Code',
                               # default=_get_default_product_code, 
                               copy=False)

    _sql_constraints = [
        ('product_product__product_code__uniq',
         'unique (product_code)',
         'Product code must be uniq!'),
    ]

    @api.multi
    def action_set_product_code(self):
        for product in self:
            if not product.product_code:
                product.write({
                    'product_code': self._get_default_product_code(product.categ_id.code),
                })
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_code = fields.Char(store=True, index=True,
                               related='product_variant_ids.product_code',
                               readonly=True, help='Product code')

    @api.multi
    def action_set_product_code(self):
        for tmpl in self.filtered(lambda r: len(r.product_variant_ids) == 1):
            tmpl.product_variant_ids[0].action_set_product_code()
        return True
