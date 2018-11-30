# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
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
    "name": "Account Extension",
    "version": "1.0",
    "author": "GALUP Sistemas",
    "description": """
        Este módulo adaptar el módulo account de odoo v9
    """,
    "license": "AGPL-3",
    "depends": ['account', 'account_check'],
    "data": [
        'data/account_payment_method_data.xml'
    ],
    'qweb': [],
    "installable": True,
    "auto_install": True,
    "active": True,
}
