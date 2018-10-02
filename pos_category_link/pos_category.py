# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.exceptions import except_orm, UserError, ValidationError, Warning

class ProductCategory(models.Model):
    _inherit = "product.category"

    code = fields.Char(size=4)
    pos_categ_id = fields.Many2one('pos.category','Point of Sale Category')

class ProductTemplate(models.Model):
    _inherit = 'product.template'    

    pos_categ_id = fields.Many2one('pos.category','Point of Sale Category', help="Those categories are used to group similar products for point of sale.", required=True)

    @api.onchange('categ_id')
    def on_change_categ_id(self):
        self.pos_categ_id = self.categ_id.pos_categ_id

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange('categ_id')
    def on_change_categ_id(self):
        self.pos_categ_id = self.categ_id.pos_categ_id        

