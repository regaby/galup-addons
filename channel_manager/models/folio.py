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

    def get_xml(self,state):
        reservation = self.env['hotel.reservation']
        xml = reservation.get_header()
        # for line2 in self.room_lines:
        for line in self.room_lines:
            room_type = self.env['hotel.room.type'].search([('cat_id','=',line.categ_id.id)])
            price = line.order_line_id.price_unit
            pax = self.guest_lines and len(self.guest_lines) or 1
            if int(room_type.room_type_id) > 0:
                xml += reservation.get_line(self.checkin_date[0:10], self.checkout_date[0:10], room_type.room_type_id, \
                                      pax, price, self.partner_id.name, self.bb_id, state)
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
        return res

