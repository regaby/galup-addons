# -*- coding: utf-8 -*-
# Copyright 2016 Openworx, LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Avemar Backend Theme",
    "summary": "Avemar backend theme",
    "version": "9.0.6",
    "category": "Themes/Backend",
    "website": "http://www.galup.com.ar",
	"description": """
                Backend theme for Odoo 9.0 Avemar Hotel.
    """,
        'images':[
        'images/screen.png'
        ],
    "author": "GALUP Sistemas",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'web',
    ],
    "data": [
        'views/assets.xml',
        'views/web.xml',
    ],
}

