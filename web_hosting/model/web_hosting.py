# -*- encoding: utf-8 -*-
##############################################################################
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp import models, fields, api, _


class WebHostingDomain(models.Model):

    _name= 'web.hosting.domain'

    name = fields.Char(size=100, sring="Domain", required=True)
    start_date = fields.Date('Start Date', required=True)
    free = fields.Boolean('Free')
    subdomain = fields.Boolean('Subdomain')
    password = fields.Char(size=100, sring="Password")
    state = fields.Selection([('unpaid','No pagado'),('paid','Pagado'),('free','Gratis')],'State',default='unpaid')
    server_id = fields.Many2one('web.hosting.server','Server',required=True)
    subdomain_ids = fields.One2many('web.hosting.subdomain','domain_id','Sub domains')
    partner_id = fields.Many2one('res.partner','Partner',required=False)
    plan_ids = fields.One2many('web.hosting.plan','domain_id','Plans')


class WebHostingServer(models.Model):

    _name= 'web.hosting.server'

    name = fields.Char(size=100, sring="Domain", required=True)
    ip = fields.Char(size=100, sring="IP Address", required=True)
    domain_ids = fields.One2many('web.hosting.domain','server_id','Domains')

class WebHostingSubdomain(models.Model):

    _name= 'web.hosting.subdomain'

    name = fields.Char(size=100, sring="Sub Domain", required=True)
    domain_id = fields.Many2one('web.hosting.domain','Domain', required=True)

class WebHostingPlan(models.Model):
    _name = 'web.hosting.plan'

    product_id = fields.Many2one('product.product', 'Product', domain=[('web_hosting','=',True)],required=True)
    domain_id = fields.Many2one('web.hosting.domain', 'Domain',required=True)
    state = fields.Selection([('unpaid','Unpaid'),('paid','Paid')],'State',default='unpaid',required=True)
    period = fields.Selection([('annual','Annual')],'Period', default='annual',required=True)
    start_date = fields.Date('Start Date', required=True)
    due_date = fields.Date('Due Date', required=True)
    paid_date = fields.Date('Paid Date', required=False)


