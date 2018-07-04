# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from openerp import models, fields, api, exceptions, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, UserError, ValidationError
from openerp import tools
import requests
from openerp.exceptions import UserError


class ChannelManager(models.Model):
    _name = "channel.manager"

    name = fields.Char(string='Nombre', required=True)
    xml_name = fields.Char(string='Nombre XML', required=True)
    xml_id = fields.Char(string='Id XML', required=True)

    @api.multi
    def test(self):
        config_obj = self.env['channel.manager.config.settings']
        config = config_obj.search([],order="id desc",limit=1)
        xml = """xml=<?xml version="1.0" encoding="UTF-8"?>
          <GetAllBookings>
          <Auth>
              <ApiKey>%s</ApiKey>
        <PropertyId>%s</PropertyId>
          </Auth>
         </GetAllBookings>"""%(config.apikey,config.property_id)
        print xml
        print '\n'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'} # set what your server accepts
        msg = requests.post('https://www.octorate.com/api/live/callApi.php?method=GetAllBookings', data=xml, headers=headers).text
        raise UserError(msg)

