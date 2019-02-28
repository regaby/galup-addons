# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
# from zklib import zklib
import requests
from openerp.exceptions import UserError
from lxml import etree


class HotelReservation(models.Model):

    _name = "hotel.reservation"
    _inherit = "hotel.reservation"



    res_id = fields.Char('ResId')
    bb_id = fields.Char('BbliverateId')

    channel_manager_id = fields.Many2one('channel.manager', 'Portal')
    xml_request = fields.Text('Solicitud Channel Manager', readonly=True)
    xml_response = fields.Text('Respuesta Channel Manager', readonly=True)
    no_migrar = fields.Boolean('No migrar')
    dolar = fields.Float('Subtotal (En Dolares)', readonly=True)

    def get_header(self):
        config_obj = self.env['channel.manager.config.settings']
        config = config_obj.search([],order="id desc",limit=1)
        xml = """xml=<?xml version="1.0" encoding="UTF-8"?>
  <BookReservationRequest>
  <Auth>
      <ApiKey>%s</ApiKey>
      <PropertyId>%s</PropertyId>
  </Auth>
  <Reservations>"""%(config.apikey,config.property_id)
        return xml

    def get_line(self, checkin_date, checkout_date, room_type_id, pax, price, partner_name, bb_id, state):
        xml = """\n<Reservation>
              <From>%s</From>
              <To>%s</To>
              <Rooms>
                  <Room>
                     <Recordid></Recordid>
                     <Roomid>%s</Roomid>"""%(checkin_date, checkout_date, room_type_id)
        if state=="Confirmed":
            xml+="""\n<Pax>%s</Pax>
                     <Total>%s</Total>
                     <Guestname>%s</Guestname>
                     <Comment></Comment>
                     <Telephone></Telephone>
                     <Provenienza></Provenienza>
                     <Cardtype></Cardtype>
                     <Cardholder></Cardholder>
                     <Cardnumber></Cardnumber>
                     <Cardexpiry></Cardexpiry>
                     <Cvv></Cvv>
                     <Submitby></Submitby>"""%(pax, price, partner_name)
        else:
            xml+="""\n<Bbliverateresvid>%s</Bbliverateresvid>"""%(bb_id)
        xml+="""\n<Status>%s</Status>
                  </Room>
              </Rooms>
              </Reservation>"""%(state)
        return xml

    def get_footer(self):
        xml = """\n</Reservations>
 </BookReservationRequest>"""
        return xml

    def send_msg(self, xml):
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'} # set what your server accepts
        msg = requests.post('https://www.octorate.com/api/live/callApi.php?method=bookreservation', data=xml, headers=headers).text.encode('utf-8')
        return msg

    def get_xml(self,state):
        xml = self.get_header()
        for line2 in self.reservation_line:
            for line in line2.reserve:
                room_type = self.env['hotel.room.type'].search([('cat_id','=',line.categ_id.id)])
                price=0
                if line2.list_price:
                    price = line2.list_price
                else:
                    price = line.price
                chout_date = self.checkout_date
                if self.checkout_hour > 10: # es late checkout, entonces sumo 1 dia
                    chout_date = (datetime.strptime(chout_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                chin_date = self.checkin_date
                if self.checkin_hour < 12: # es early checkin, entonces resto 1 dia
                    chin_date = (datetime.strptime(chin_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                if int(room_type.room_type_id) > 0:
                    xml += self.get_line(chin_date, chout_date, room_type.room_type_id, \
                                          self.adults, price, self.partner_id.name, self.bb_id, state)
        xml += self.get_footer()
        self.xml_request = xml
        msg = self.send_msg(xml)
        self.xml_response = msg
        root = etree.fromstring(msg)
        process_list = root.findall('RoomUpdateMessage', root.nsmap)
        for process in process_list:
            for child in process:
                if child.xpath('local-name()') == 'Bbliverateresvid':
                    self.bb_id = child.text
        return xml

    @api.multi
    def confirmed_reservation(self):
        res = super(HotelReservation, self).confirmed_reservation()
        if not self.res_id:
            xml = self.get_xml('Confirmed')
        return res

    @api.multi
    def cancel_reservation(self):
        res = super(HotelReservation, self).cancel_reservation()
        if self.bb_id and not self.res_id:
            xml = self.get_xml('Cancelled')
        return res

    @api.multi
    def copy(self, default=None):
        '''
        @param self: object pointer
        @param default: dict of default values to be set
        '''
        default['res_id'] = False
        default['bb_id'] = False
        default['channel_manager_id'] = False
        default['xml_request'] = False
        default['xml_response'] = False
        default['no_migrar'] = False
        return super(HotelReservation, self).copy(default=default)

    @api.multi
    def _create_folio(self):
        hotel_folio_obj = self.env['hotel.folio']
        res = super(HotelReservation, self)._create_folio()
        # se creo el folio ya en estado confirmado
        print '\n\nres', res
        folio_id = res['res_id']
        folio = hotel_folio_obj.browse(folio_id)
        folio.bb_id = self.bb_id
        folio.xml_request = self.xml_request
        folio.xml_response = self.xml_response
        return res


