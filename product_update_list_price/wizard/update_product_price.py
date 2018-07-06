
from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
import urllib2
from openerp.exceptions import UserError, AccessError
from openerp.exceptions import except_orm, ValidationError


class UpdateProductPrice(models.TransientModel):
    _name = 'update.product.price'
    _description = 'update.product.price'



    
    percentage = fields.Integer('Porcentaje', required="True")
    option = fields.Selection([('sumar','Aumentar Porcentaje'),('restar','Descontar Porcentaje')],required=True,default="sumar",string="Operacion")

    @api.multi
    def action_update(self):
        if self.percentage <= 0 or self.percentage > 100:
            raise ValidationError(_('El Porcentaje debe ser entre 0% y 100%"'))
        order_obj = self.env['product.template']
        active_ids = self._context['active_ids']
        invoice_ids = []
        for a_id in active_ids:
            product = order_obj.browse(a_id)
            if self.option=="sumar":
                product.list_price = product.list_price + (product.list_price*self.percentage)/100
            else:
                product.list_price = product.list_price - (product.list_price*self.percentage)/100
    

    