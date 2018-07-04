# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
# from zklib import zklib


class HotelRoomType(models.Model):

    _name = "hotel.room.type"
    _inherit = "hotel.room.type"

    

    room_type_id = fields.Char('RoomTypeId')
    



