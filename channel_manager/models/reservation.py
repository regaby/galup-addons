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

    def get_xml(self,state):
        config_obj = self.env['channel.manager.config.settings']
        config = config_obj.search([],order="id desc",limit=1)
        xml = """xml=<?xml version="1.0" encoding="UTF-8"?>
  <BookReservationRequest>
  <Auth>
      <ApiKey>%s</ApiKey>
      <PropertyId>%s</PropertyId>
  </Auth>
  <Reservations>"""%(config.apikey,config.property_id)

        for line2 in self.reservation_line:
            for line in line2.reserve:
                print self.checkin_date, self.checkout_date, self.adults, self.amount_total, self.partner_id.name
                print line.categ_id.name
                print line.categ_id.id
                room_type = self.env['hotel.room.type'].search([('cat_id','=',line.categ_id.id)])
                price=0
                if line2.list_price:
                    price = line2.list_price
                else:
                    price = line.price
                if room_type.room_type_id:
                    xml+="""\n<Reservation>
                          <From>%s</From>
                          <To>%s</To>
                          <Rooms>
                              <Room>
                                 <Recordid></Recordid>
                                 <Roomid>%s</Roomid>"""%(self.checkin_date, self.checkout_date,room_type.room_type_id)
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
                                 <Submitby></Submitby>"""%(self.adults,price, self.partner_id.name)
                    else:
                        xml+="""\n<Bbliverateresvid>%s</Bbliverateresvid>"""%(self.bb_id)
                    xml+="""\n<Status>%s</Status>
                              </Room>
                          </Rooms>
                          </Reservation>"""%(state)
        xml+="""\n</Reservations>
 </BookReservationRequest>"""
        print xml
        self.xml_request = xml
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'} # set what your server accepts
        msg = requests.post('https://www.octorate.com/api/live/callApi.php?method=bookreservation', data=xml, headers=headers).text.encode('utf-8')
        print msg
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
        xml = self.get_xml('Confirmed')
        return res

    @api.multi
    def cancel_reservation(self):
        res = super(HotelReservation, self).cancel_reservation()
        if self.bb_id:
            xml = self.get_xml('Cancelled')
        return res

    


