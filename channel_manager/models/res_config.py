# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from openerp.osv import fields, osv
# from openerp import api, fields, models, _
import logging

from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

_logger = logging.getLogger(__name__)

class channel_manager_configuration(osv.osv):
    _name = 'channel.manager.config.settings'
    _inherit = 'res.config.settings'	
    
    _columns = {
        'apikey': fields.char('Api Key'),
        'property_id': fields.char('Property Id'),

    }

    def set_apikey(self, cr, uid, ids, context=None):
        apikey = self.browse(cr, uid, ids, context=context).apikey
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'channel.manager.config.settings', 'apikey', apikey)
        return res

    def set_property_id(self, cr, uid, ids, context=None):
        property_id = self.browse(cr, uid, ids, context=context).property_id
        res = self.pool.get('ir.values').set_default(cr, SUPERUSER_ID, 'channel.manager.config.settings', 'property_id', property_id)
        return res
    
