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
    bb_id_list = fields.One2many('channel.manager.bb.id', 'reservation_id','Bb ids')
    result_msg = fields.Text('Mensaje', readonly=True)

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

    def get_result_msg(self, res_channel_id, res_channel_msg):
        result_msg = 'Reserva %s: '%str(int(res_channel_id)+1)
        if res_channel_msg == 'Successfully inserted':
            result_msg += 'Ha sido insertada correctamente\n'
        elif res_channel_msg == 'Status Changed.':
            result_msg += 'Estado de reserva ha sido cancelado\n'
        elif res_channel_msg == 'Status Already Same.':
            result_msg += 'Error! El estado ya es el mismo\n'
        elif result_msg == 'Reservation not found.':
            result_msg += 'Error! Reserva no encontrada\n'
        else:
            result_msg += "%s\n"%res_channel_msg
        return result_msg

    def parse_msg(self, msg, vals):
        bb_id_list = []
        res_channel_id = 0
        root = etree.fromstring(msg)
        process_list = root.findall('RoomUpdateMessage', root.nsmap)
        result_msg = ''
        if not process_list:
            process_list = root.findall('Errors', root.nsmap)
        for process in process_list:
            for child in process:
                if child.xpath('local-name()') == 'Bbliverateresvid':
                    vals['bb_id'] = child.text
                    bb_id_list.append((0, 0, {
                        'bb_id': child.text,
                        }))
                if child.xpath('local-name()') == 'Recordid':
                    res_channel_id = "%s"%child.text
                if child.xpath('local-name()') in ['Succmessage', 'Errormessage', 'ErrorMsg']:
                    res_channel_msg = "%s"%child.text
                for child2 in child:
                    for child3 in child2:
                        if child3.xpath('local-name()') == 'Recordid':
                            res_channel_id = "%s"%child3.text
                        if child3.xpath('local-name()') in ['Succmessage', 'Errormessage']:
                            res_channel_msg = "%s"%child3.text
                    result_msg += self.get_result_msg(res_channel_id, res_channel_msg)
            result_msg += self.get_result_msg(res_channel_id, res_channel_msg)
        vals['result_msg'] = result_msg
        vals['xml_response'] = msg
        if bb_id_list:
            vals['bb_id_list'] = bb_id_list
        return vals

    def get_xml(self,state):
        vals = {}
        xml = self.get_header()
        i = 0
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
                    bb_id = self.bb_id_list and self.bb_id_list[i].bb_id or self.bb_id
                    i += 1
                    xml += self.get_line(chin_date, chout_date, room_type.room_type_id, \
                                          self.adults, price, self.partner_id.name, bb_id, state)
        xml += self.get_footer()
        vals['xml_request'] = xml
        msg = self.send_msg(xml)
        vals = self.parse_msg(msg, vals)
        self.write(vals)
        return xml

    @api.multi
    def confirmed_reservation(self):
        res = super(HotelReservation, self).confirmed_reservation()
        if not self.res_id:
            self.result_msg = False
            xml = self.get_xml('Confirmed')
        return res

    @api.multi
    def cancel_reservation(self):
        res = super(HotelReservation, self).cancel_reservation()
        # if self.bb_id and not self.res_id:
        # quito la comprobación res_id ya que no se estaban cancelado las reservas que venian del channel.
        if self.bb_id:
            self.result_msg = False
            xml = self.get_xml('Cancelled')
            # borro res_id ya que luego no se confirmaba reserva si estaba este valor seteado (linea 157)
            self.res_id = False
            self.bb_id_list = False
        return res

    def set_to_draft_reservation(self):
        res = super(HotelReservation, self).set_to_draft_reservation()
        self.result_msg = False
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
        default['bb_id_list'] = False
        return super(HotelReservation, self).copy(default=default)

    @api.multi
    def _create_folio(self):
        hotel_folio_obj = self.env['hotel.folio']
        res = super(HotelReservation, self)._create_folio()
        # se creo el folio ya en estado confirmado
        print '\n\nres', res
        folio_id = res['res_id']
        folio = hotel_folio_obj.browse(folio_id)
        folio.bb_id = self.bb_id ## esto se debe copiar ya que sino no se realizan los envios al channel!
        folio.xml_request = self.xml_request
        folio.xml_response = self.xml_response
        folio.bb_id_list = self.bb_id_list
        return res

class bb_id(models.Model):

    _name = 'channel.manager.bb.id'

    bb_id = fields.Char('BbliverateId')
    reservation_id = fields.Many2one('hotel.reservation', string='Reserva',
                               ondelete='cascade')
    folio_id = fields.Many2one('hotel.folio', string='Folio',
                               ondelete='cascade')
