# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
# from zklib import zklib
import requests
from openerp.exceptions import UserError
from lxml import etree

class HotelFolio(models.Model):

    _name = 'hotel.folio'
    _inherit = 'hotel.folio'

    bb_id = fields.Char('BbliverateId')
    xml_request = fields.Text('Solicitud Channel Manager', readonly=True)
    xml_response = fields.Text('Respuesta Channel Manager', readonly=True)
    bb_id_list = fields.One2many('channel.manager.bb.id', 'folio_id','Bb ids')

    def get_xml(self,state):
        reservation = self.env['hotel.reservation']
        xml = reservation.get_header()
        i = 0
        bb_id_list = []
        # for line2 in self.room_lines:
        for line in self.room_lines:
            room_type = self.env['hotel.room.type'].search([('cat_id','=',line.categ_id.id)])
            price = line.order_line_id.price_unit
            pax = self.guest_lines and len(self.guest_lines) or 1
            chout_date = self.checkout_date[0:10]
            if self.late_checkout and self.late_checkout_hour > 10: # es late checkout, entonces sumo 1 dia
                chout_date = (datetime.strptime(chout_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            chin_date = self.checkin_date[0:10]
            if self.early_checkin and self.early_checkin_hour < 12: # es early checkin, entonces resto 1 dia
                chin_date = (datetime.strptime(chin_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            if int(room_type.room_type_id) > 0:
                bb_id = self.bb_id_list and self.bb_id_list[i].bb_id or self.bb_id
                i += 1
                xml += reservation.get_line(chin_date, chout_date, room_type.room_type_id, \
                                      pax, price, self.partner_id.name, bb_id, state)
        xml += reservation.get_footer()
        self.xml_request = xml
        msg = reservation.send_msg(xml)
        self.xml_response = msg
        root = etree.fromstring(msg)
        process_list = root.findall('RoomUpdateMessage', root.nsmap)
        for process in process_list:
            for child in process:
                if child.xpath('local-name()') == 'Bbliverateresvid':
                    self.bb_id = child.text
                    bb_id_list.append((0, 0, {
                        'bb_id': child.text,
                        }))
        if bb_id_list:
            self.bb_id_list = bb_id_list
        return xml

    @api.multi
    def action_confirm(self):
        res = super(HotelFolio, self).action_confirm()
        if not self.reservation_id or self.bb_id:
            xml = self.get_xml('Confirmed')
        return res

    @api.multi
    def action_cancel(self):
        res = super(HotelFolio, self).action_cancel()
        if not self.reservation_id or self.bb_id:
            xml = self.get_xml('Cancelled')
            self.bb_id_list = False
        return res

