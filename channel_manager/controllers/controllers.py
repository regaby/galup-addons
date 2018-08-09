# -*- coding: utf-8 -*-
from openerp import http
import requests
import json
from openerp.http import Response
import logging
_logger = logging.getLogger(__name__)
from openerp.http import request
from lxml import etree


class Home(http.Controller):
    @http.route('/test', type='http', auth="public", csrf=False)
    def test(self, **kwargs):
        config_obj = request.env['channel.manager.config.settings']
        config = config_obj.sudo().search([])
        print config

        data = kwargs 
        print kwargs
        _logger.info(kwargs)
        xml="""xml=<?xml version="1.0" encoding="UTF-8"?>
  <GetBookings>
  <Auth>
<ApiKey>%s</ApiKey>
     <PropertyId>%s</PropertyId>
  </Auth>

      <ReservationId>%s</ReservationId>
 </GetBookings>
        """%('a7e80fc2a07ac2661bf20b020ba0b135',data['propertyid'],data['reservationid'])
        print xml
        print '\n'
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'} # set what your server accepts
        msg = requests.post('https://www.octorate.com/api/live/callApi.php?method=GetBookings', data=xml, headers=headers).text.encode('utf-8')
        print msg
        vals = {}
        lines = []
        line = {}
        vals_lines = []
        reservation_obj = request.env['hotel.reservation']

        if data['status'] in ['modification','new']:
            reservation = reservation_obj.sudo().search([('res_id','=',data['reservationid'])])
            # control porque se mandan tres veces las reservas...
            if reservation:
                # si ya esta creada le zafo
                return Response("TEST",content_type='text/html;charset=utf-8',status=500)
            root = etree.fromstring(msg)
            process_list = root.findall('Bookings', root.nsmap)
            pax = 0
            for process in process_list:
                for child2 in process:
                    for child in child2:
                        if child.xpath('local-name()') == 'Channel':
                            vals['channel'] = child.text
                        if child.xpath('local-name()') == 'StartDate':
                            vals['checkin_date'] = child.text
                        if child.xpath('local-name()') == 'EndDate':
                            vals['checkout_date'] = child.text
                        if child.xpath('local-name()') == 'BbliverateId':
                            vals['bb_id'] = child.text
                        if child.xpath('local-name()') == 'ResId':
                            vals['res_id'] = child.text
                        if child.xpath('local-name()') == 'BbliverateTimestamp':
                            vals['create_date'] = child.text # aparentemente tiene 5 horas de diferencia
                        # TODO: ResSource creo qe va a traer la info si es booking o expedia...
                        # if child.xpath('local-name()') == 'Customers':
                        for cus2 in child:
                            line={}
                            for cus in cus2:
                                if cus.xpath('local-name()') == 'CustomerFName':
                                    vals['partner_name'] = cus.text.upper()
                                if cus.xpath('local-name()') == 'CustomerEmail':
                                    vals['partner_email'] = cus.text
                                if cus.xpath('local-name()') == 'CustomerPhone':
                                    vals['partner_phone'] = cus.text
                                if cus.xpath('local-name()') == 'CustomerNote':
                                    vals['observations'] = cus.text
                                if cus.xpath('local-name()') == 'Pax':
                                        pax += int(cus.text)
                                if cus.xpath('local-name()') == 'Units':
                                    line['cantidad'] = cus.text
                                if cus.xpath('local-name()') == 'Price':
                                        line['price'] = cus.text
                                for ccus in cus:
                                    if ccus.xpath('local-name()') == 'Price':
                                        line['price'] = ccus.text
                                    if ccus.xpath('local-name()') == 'RoomTypeId':
                                        line['room_type_id'] = ccus.text
                                    if ccus.xpath('local-name()') == 'Units':
                                        line['cantidad'] = ccus.text
                            if len(line)>0:
                                lines.append(line)
            vals['adults'] = pax
            partner_obj = request.env['res.partner'].sudo()
            partner = partner_obj.search([('name','=',vals['partner_name'])])
            if 'channel' in vals.keys():
                channel_obj = request.env['channel.manager'].sudo()
                channel = channel_obj.search([('xml_id','=',vals['channel'])])
                vals['channel_manager_id'] = channel.id
            vals['pricelist_id'] = request.env['product.pricelist'].sudo().search([]).id
            vals['checkin_hour'] = 15
            vals['checkout_hour'] = 13
            vals['checkin'] = '%s %s:00:00'%(vals['checkin_date'], vals['checkin_hour'])
            vals['checkout'] = '%s %s:00:00'%(vals['checkout_date'], vals['checkout_hour'])
            vals['state'] = 'draft'
            vals['xml_request'] = data
            vals['xml_response'] = msg
            if not partner:
                partner = partner_obj.create({'name' : vals['partner_name'], 
                                              'email': 'partner_email' in vals.keys() and vals['partner_email'], 
                                              'phone': 'partner_phone' in vals.keys() and vals['partner_phone'], 
                                              'customer': True})
            vals['partner_id'] = partner.id
            rcateg_id = []
            ocupadas = []
            for l in lines:
                _logger.info(l['room_type_id'])
                rtype = request.env['hotel.room.type'].sudo().search([('room_type_id','=',l['room_type_id'])])
                _logger.info(rtype)
                rcateg_id.append(rtype.cat_id.id)
            summary_obj = request.env['room.reservation.summary']
            res = summary_obj.sudo().check_reservation(rcateg_id, '%s 12:00:00'%vals['checkin_date'], '%s 10:00:00'%vals['checkout_date'])

            for l in lines:
                ## chequeo disponibilidad...
                for r in res['room_summary']:
                    print r
                    free_room_id =r['value'][0]['room_id'] 
                    if free_room_id in ocupadas:
                        continue
                    libre = True
                    for v in r['value']:
                        if v['state']!='Libre':
                            libre=False
                    if libre == True:
                        break
                if libre == True:
                    print 'habitacion libre', free_room_id
                    ocupadas.append(free_room_id)
                else:
                    print 'no hay hab. libres'
                print free_room_id
                vals_lines.append((0, 0, {
                            'list_price': l['price'],
                            'reserve' : [(6,0,[free_room_id])],
                        }))
            vals['reservation_line'] = vals_lines
            reservation = reservation_obj.sudo().create(vals)
            try:
                reservation.confirmed_reservation()
            except Exception, e:
                _logger.info(e)
        else:
            # cancelo reserva
            reservation = reservation_obj.sudo().search([('res_id','=',data['reservationid'])])
            if reservation:
                reservation.state = 'cancel'

        return Response("TEST",content_type='text/html;charset=utf-8',status=500)
