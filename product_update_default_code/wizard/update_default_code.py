
from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
import urllib2
from openerp.exceptions import UserError, AccessError
from openerp.exceptions import except_orm, ValidationError


class UpdateDefaultCode(models.TransientModel):
    _name = 'update.default.code'
    _description = 'update.default.code'

    # percentage = fields.Integer('Porcentaje', required="True")
    # option = fields.Selection([('sumar','Aumentar Porcentaje'),('restar','Descontar Porcentaje')],required=True,default="sumar",string="Operacion")

    @api.multi
    def action_update(self):
        # if self.percentage <= 0 or self.percentage > 100:
        #     raise ValidationError(_('El Porcentaje debe ser entre 0% y 100%"'))
        order_obj = self.env['product.template']
        active_ids = self._context['active_ids']
        for a_id in active_ids:
            product = order_obj.browse(a_id)
            if not product.default_code:
                product.action_set_product_code()
            # if self.option=="sumar":
            #     product.list_price = product.list_price + (product.list_price*self.percentage)/100
            # else:
            #     product.list_price = product.list_price - (product.list_price*self.percentage)/100



