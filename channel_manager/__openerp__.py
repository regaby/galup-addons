# -*- coding: utf-8 -*-

{
    "name": "Channel Manager",
    "version": "1.0",
    "author": "Galup Sistemas",
    "category": "Custom",
    "website": "galup.com.ar",
    "description": "A Module for Octorate channel manager integration",
    "depends": [
        "base",
        "galup_hotel",
    ],
    "init_xml": [
    ],
    "data": [
        ##security
        'security/channel_manager_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'views/channel_manager_view.xml',
        'views/reservation_view.xml',
        'views/room_type_view.xml',
        ##data
        'data/channel_manager_data.xml',
    ],
    "active": False,
    "installable": True
}

