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
          <GetRoomTypes>
              <ApiKey>%s</ApiKey>
        <PropertyId>%s</PropertyId>
         </GetRoomTypes>"""%(config.apikey,config.property_id)
        print xml
        print '\n'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'} # set what your server accepts
        msg = requests.post('https://www.octorate.com/api/live/callApi.php?method=GetRoomTypes', data=xml, headers=headers).text
        raise UserError(msg)

    @api.multi
    def test2(self):
        # reserva Christiana perin gaier, no entro por restriccion de cantidad de pasajeros por habitacion
        xml = {'status': u'new', 'reservationid': u'3822998540', 'siteid': u'142', 'site': u'booking_xml', 'propertyid': u'616123'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        msg = requests.post('http://localhost:8069/test', data=xml, headers=headers).text
        raise UserError(msg)

    @api.multi
    def test3(self):
        reservation_obj = self.env['hotel.reservation']
        current_date =  str(datetime.now())[0:10]
        res = reservation_obj.search([('checkin_date','>=',current_date),('state','=','confirm'),('no_migrar','=',False)])
        for r in res:
            xml = r.get_xml('Confirmed')
            print xml
        print 'fin del proceso....'


