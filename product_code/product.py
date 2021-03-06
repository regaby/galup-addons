# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import except_orm, UserError, ValidationError

class ProductCategory(models.Model):
    _inherit = "product.category"

    code = fields.Char(size=4)

    @api.model
    def create(self, vals):
        ## code required
        if 'code' in vals.keys():
            if not vals['code']:
                raise UserError('El código de categoría es un campo obligatorio')
        ## create sequence
        sequence = {
            'name': vals['name'],
            'code': vals['code'],
            'prefix': vals['code'],
            'padding': 5,
            'number_increment': 1,
            'number_next_actual': 1,
            'implementation': 'standard'
        }
        seq_id = self.env['ir.sequence'].create(sequence)
        return super(ProductCategory, self).create(vals)

    _sql_constraints = [
        ('product_category_code_uniq',
         'unique (code)',
         'El código de categoría de producto debe ser único!'),
        ('product_category_name_uniq',
         'unique (name)',
         'El nombre de categoría de producto debe ser único!'),
    ]


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_default_product_code(self, code):
        return self.env['ir.sequence'].get(code)

    @api.model
    def create(self, vals):
        code = False
        if 'product_tmpl_id' in vals:
            tmp = self.env['product.template'].browse(vals['product_tmpl_id'])
            code = tmp.categ_id.code
        if 'categ_id' in vals:
            categ_id = self.env['product.category'].browse(vals['categ_id'])
            code = categ_id.code
        if code:
            vals['default_code'] = self._get_default_product_code(code)
        return super(ProductProduct, self).create(vals)

    @api.multi
    def write(self, vals):
        code = False
        if 'categ_id' in vals:
            categ_id = self.env['product.category'].browse(vals['categ_id'])
            code = categ_id.code
        if code:
            vals['default_code'] = self._get_default_product_code(code)
        return super(ProductProduct, self).write(vals)

    _sql_constraints = [
        ('product_product__default_code__uniq',
         'unique (default_code)',
         'Product code must be uniq!'),
        ('product_product__default_name__uniq',
         'unique (name_template)',
         'El nombre del producto debe ser unico!'),
    ]

    @api.multi
    def action_set_product_code(self):
        for product in self:
            if not product.default_code:
                if product.categ_id.code:
                    product.write({
                        'default_code': self._get_default_product_code(product.categ_id.code),
                    })
                else:
                    raise UserError('Debe seleccionar una categoria de producto con una secuencia asociada')
        return True


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def action_set_product_code(self):
        for tmpl in self.filtered(lambda r: len(r.product_variant_ids) == 1):
            tmpl.product_variant_ids[0].action_set_product_code()
        return True

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"


    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            tmp = self.env['product.product'].browse(vals['product_id'])
            if not tmp.default_code:
                raise UserError('El producto %s no tiene categoria asociada'%(tmp.name))
        return super(PurchaseOrderLine, self).create(vals)

