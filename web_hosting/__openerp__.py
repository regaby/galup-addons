# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2017 Soltic S.R.L 
#    All Rights Reserved.
#    
############################################################################
#    
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Web Hosting",
    "version": "1.0",
    "author": "Huerta Grafica",
    "category": "",
    "description": """
        Web Hosting Huerta Grafica
    """,
    "license": "AGPL-3",
    "depends": ['base','product'],
    "data": [
        # security
        'security/web_hosting_security.xml',
        'security/ir.model.access.csv',
        # view
        'view/web_hosting_view.xml',
        'view/server_view.xml',
        'view/product_view.xml',
        'view/plan_view.xml',
        # data
        'data/data.xml',
# menu
        'view/menu_view.xml',
    ],
    "installable": True,
    "active": False,
}