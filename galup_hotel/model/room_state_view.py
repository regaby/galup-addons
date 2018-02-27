# -*- coding: utf-8 -*-

from openerp import tools
from openerp import models, fields, api


class HotelRoomStateView(models.Model):
    _name = "hotel.room.state.view"
    _description = "Room State"
    _auto = False
    _rec_name = 'name'

    room_id = fields.Many2one('hotel.room', string='Habitacion', readonly=True)
    status = fields.Selection([('available', 'Disponible'), ('occupied', 'Ocupada'),('blocked', 'Bloqueado')],'Estado', readonly=True)
    state = fields.Selection([('clean', 'Limpia'), ('dirty', 'Sucia'),],'Limpieza', readonly=True)
    categ_id = fields.Many2one('product.category', string='Categoria', readonly=True)
    checkin_hour = fields.Char('Hora de Entrada')
    reserva_partner_id = fields.Many2one('res.partner', string='Huesped Reserva', readonly=True)
    folio_id = fields.Many2one('hotel.folio', string='Folio', readonly=True)
    folio_partner_id = fields.Many2one('res.partner', string='Huesped Folio', readonly=True)
    folio_name = fields.Char(string='Folio', readonly=True)
    folio_state = fields.Selection([
            ('draft','Factura en Borrador'),
            ('proforma', 'Pro-forma'),
            ('proforma2', 'Pro-forma'),
            ('open', 'Factura Validada'),
            ('paid', 'Factura Pagada'),
            ('cancel', 'Cancelado'),
        ], string='Estado de Deuda', readonly=True)
    pax = fields.Integer('Capacidad', readonly=True)
    checkout_hour = fields.Char('Salida')
    name = fields.Char('Name')

    _order = 'name asc'

    def init(self, cr):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW hotel_room_state_view as (
            select  hr.id, hr.id as room_id , pt.name as name, hr.status, hr.state , pt.categ_id, pc.name as categ_name, reserva.checkin_hour, reserva.name as reserva_name , 
                reserva.partner_id as reserva_partner_id, folio.folio_id, 
                folio.partner_name as partner, folio.partner_id as folio_partner_id, folio.name as folio_name, folio.pax, folio.state as folio_state, folio.checkout_hour
                from hotel_room hr 
                join product_product pp on (hr.product_id=pp.id)
                join product_template pt on (pp.product_tmpl_id=pt.id)
                join product_category pc on (pt.categ_id=pc.id)
                left join (select check_in::time - '03:00:00'::time as checkin_hour, room_id , rp.name, hr.partner_id
                    from hotel_room_reservation_line  hrrl
                    join hotel_reservation hr on (hrrl.reservation_id=hr.id)
                    join res_partner rp on (rp.id=hr.partner_id)
                    where check_in::date = now()::date and hrrl.state='assigned') reserva on (reserva.room_id = hr.id)
                left join (select frl.room_id, so.partner_id, rp.name as partner_name, hf.name, coalesce(guest.count,0) + 1 as PAX, ai.state, hf.id as folio_id, 
                        --case when check_out::date = now()::date then check_out::time - '03:00:00'::time  end as checkout_hour
                        check_out as checkout_hour
                    from folio_room_line frl
                    join hotel_folio hf on (frl.folio_id = hf.id)
                    join sale_order so on (hf.order_id=so.id)
                    join res_partner rp on (rp.id=so.partner_id)
                    left join (select folio_id, count(*) from hotel_guest group by folio_id) guest on (guest.folio_id = hf.id)
                    left join account_invoice ai on (hf.hotel_invoice_id = ai.id)
                    where check_in::date <= now()::date
                    and so.state not in ('done','cancel')
                    and check_out::date >= now()::date) folio on (folio.room_id = hr.id)
        )""" )
